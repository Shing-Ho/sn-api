import decimal
from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest

from api.booking import booking_service
from api.booking.booking_model import Payment, HotelBookingRequest, Customer, Traveler, PaymentMethod, SubmitErrorType
from api.common import cache_storage
from api.common.models import RoomOccupancy, RoomRate, RateType, Address
from api.hotel import hotel_service
from api.hotel.adapters.priceline.priceline_info import PricelineInfo
from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.hotel_model import HotelLocationSearch
from api.models import models
from api.models.models import Booking, BookingStatus, HotelBooking
from api.tests import to_money, test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.view.exceptions import PaymentException


class TestBookingService(SimplenightTestCase):
    def test_booking_request_validation(self):
        address = {
            "city": "San Francisco",
            "province": "CA",
            "postal_code": "94111",
            "country": "US",
            "address1": "One Market Street",
        }

        with pytest.raises(ValueError) as e:
            Payment.Schema().load({"payment_method": "CREDIT_CARD", "billing_address": address})

        self.assertIn("Must set payment_card_parameters when payment_method is CREDIT_CARD", str(e))

        with pytest.raises(ValueError) as e:
            Payment.Schema().load({"payment_method": "PAYMENT_TOKEN", "billing_address": address})

        self.assertIn("Must set payment_token when payment_method is PAYMENT_TOKEN", str(e))

    def test_stub_booking(self):
        booking_request = HotelBookingRequest(
            api_version=1,
            transaction_id="foo",
            hotel_id="ABC123",
            checkin=date(2020, 1, 1),
            checkout=date(2020, 1, 1),
            language="en_US",
            customer=Customer(
                first_name="John", last_name="Doe", phone_number="5558675309", email="john@doe.foo", country="US"
            ),
            traveler=Traveler("John", "Doe", occupancy=RoomOccupancy(adults=1)),
            room_rates=[
                RoomRate(
                    code="foo-rate-key",
                    rate_plan_code="foo",
                    room_type_code="bar",
                    rate_type=RateType.BOOKABLE,
                    total_base_rate=to_money("100.99"),
                    total_tax_rate=to_money("20.00"),
                    total=to_money("120.99"),
                    daily_rates=[],
                    maximum_allowed_occupancy=RoomOccupancy(),
                )
            ],
            payment=Payment(
                billing_address=Address(
                    city="San Francisco", province="CA", postal_code="94111", country="US", address1="One Market Street"
                ),
                payment_method=PaymentMethod.PAYMENT_TOKEN,
                payment_token="token_foo",
            ),
            provider=StubHotelAdapter.PROVIDER_NAME,
        )

        cache_storage.set("foo-rate-key", booking_request.room_rates[0])

        with patch("api.payments.payment_service.authorize_payment"):
            response = booking_service.book(booking_request)

        self.assertEqual(1, response.api_version)
        self.assertIsNotNone(response.transaction_id)
        self.assertTrue(response.status.success)
        self.assertEqual("Success", response.status.message)
        self.assertEqual("ABC123", response.reservation.hotel_id)
        self.assertIsNotNone(response.reservation.locator)
        self.assertEqual("2020-01-01", str(response.reservation.checkin))
        self.assertEqual("2020-01-01", str(response.reservation.checkout))
        self.assertEqual("John", response.reservation.customer.first_name)
        self.assertEqual("Doe", response.reservation.customer.last_name)
        self.assertEqual("5558675309", response.reservation.customer.phone_number)

        booking = Booking.objects.get(transaction_id=response.transaction_id)
        self.assertEqual(response.transaction_id, booking.transaction_id)
        self.assertIsNotNone(booking.booking_id)
        self.assertEqual(BookingStatus.BOOKED.value, booking.booking_status)

        self.assertEqual("John", booking.lead_traveler.first_name)
        self.assertEqual("Doe", booking.lead_traveler.last_name)
        self.assertEqual("US", booking.lead_traveler.country)
        self.assertEqual("john@doe.foo", booking.lead_traveler.email_address)
        self.assertEqual("5558675309", booking.lead_traveler.phone_number)

        hotel_bookings = models.HotelBooking.objects.filter(booking__booking_id=booking.booking_id)

        self.assertEqual("Hotel Name", hotel_bookings[0].hotel_name)
        self.assertEqual("stub", hotel_bookings[0].provider_name)
        self.assertEqual("ABC123", hotel_bookings[0].hotel_code)
        self.assertIsNotNone("foo", hotel_bookings[0].record_locator)
        self.assertEqual(decimal.Decimal("120.99"), hotel_bookings[0].total_price)
        self.assertEqual("USD", hotel_bookings[0].currency)

    def test_stub_booking_with_invalid_payment(self):
        invalid_card_number_payment = test_objects.payment("4000000000000002")
        booking_request = test_objects.booking_request(payment_obj=invalid_card_number_payment)

        with pytest.raises(PaymentException) as e:
            booking_service.book(booking_request)

        assert e.value.error_type == SubmitErrorType.PAYMENT_DECLINED

    def test_hotelbeds_booking(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin,
            end_date=checkout,
            occupancy=RoomOccupancy(adults=1),
            location_id="SFO",
            provider="hotelbeds",
        )

        availability_response = hotel_service.search_by_location(search)

        # Find first hotel with a bookable rate
        room_to_book = None
        for hotel in availability_response:
            for room in hotel.room_types:
                if room.rate_type == RateType.BOOKABLE:
                    room_to_book = room
                    break

        self.assertIsNotNone(room_to_book)

        booking_request = test_objects.booking_request(provider="hotelbeds", rate_code=room_to_book)
        booking_response = booking_service.book(booking_request)

        provider_rate: RoomRate = cache_storage.get(room_to_book.code)
        assert booking_response.reservation.room_rates[0].code == provider_rate.code

        hotel_booking = HotelBooking.objects.filter(record_locator=booking_response.reservation.locator.id).first()
        assert hotel_booking.provider_total == provider_rate.total.amount
        assert hotel_booking.total_price == room_to_book.total.amount

    def test_priceline_booking(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin,
            end_date=checkout,
            occupancy=RoomOccupancy(adults=1),
            location_id="5391959",
            provider="priceline",
        )

        availability_response = hotel_service.search_by_location(search)
        self.assertTrue(len(availability_response) >= 1)
        self.assertTrue(len(availability_response[0].room_types) >= 1)

        hotel_to_book = availability_response[0]
        room_to_book = hotel_to_book.room_types[0]
        booking_request = test_objects.booking_request(provider=PricelineInfo.name, rate_code=room_to_book)
        booking_response = booking_service.book(booking_request)

        print(booking_response)
