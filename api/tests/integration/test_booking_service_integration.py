import decimal
import uuid
from collections import Sequence
from datetime import datetime, date
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from stripe.error import CardError

from api.hotel.models.hotel_common_models import RoomOccupancy, Address
from api.hotel import hotel_cache_service, booking_service
from api.hotel.models import booking_model
from api.hotel.models.booking_model import (
    Payment,
    HotelBookingRequest,
    Customer,
    PaymentMethod,
    SubmitErrorType,
)
from api.hotel.models.hotel_api_model import CancellationSummary, CancelRequest
from api.models import models
from api.models.models import (
    Booking,
    BookingStatus,
    PaymentTransaction,
    Provider,
    Traveler,
    HotelBooking,
    HotelCancellationPolicy,
    ProviderHotel,
)
from api.tests import test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.view.exceptions import PaymentException, BookingException


class TestBookingServiceIntegration(SimplenightTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.provider = Provider.objects.get_or_create(name="stub")[0]

    def test_stub_booking(self):
        booking_request = HotelBookingRequest(
            api_version=1,
            transaction_id="foo",
            hotel_id="ABC123",
            language="en_US",
            customer=Customer(
                first_name="John", last_name="Doe", phone_number="5558675309", email="john@doe.foo", country="US"
            ),
            traveler=booking_model.Traveler(first_name="John", last_name="Doe", occupancy=RoomOccupancy(adults=1)),
            room_code="sn-foo",
            payment=Payment(
                billing_address=Address(
                    city="San Francisco", province="CA", postal_code="94111", country="US", address1="One Market Street"
                ),
                payment_method=PaymentMethod.PAYMENT_TOKEN,
                payment_token="token_foo",
            ),
        )

        room_rate = test_objects.room_rate("foo", "100.0", base_rate="80", tax_rate="20")
        simplenight_rate = test_objects.room_rate("sn-foo", "120", base_rate="96", tax_rate="24")
        hotel = test_objects.hotel()

        hotel_cache_service.save_provider_rate_in_cache(
            hotel=hotel, room_rate=room_rate, simplenight_rate=simplenight_rate
        )

        with patch("api.payments.payment_service.authorize_payment"):
            response = booking_service.book(booking_request)

        self.assertEqual(1, response.api_version)
        self.assertIsNotNone(response.transaction_id)
        self.assertTrue(response.status.success)
        self.assertEqual("success", response.status.message)
        self.assertEqual("100", response.reservation.hotel_id)
        self.assertIsNotNone(response.reservation.locator)
        self.assertEqual("2020-01-01", str(response.reservation.checkin))
        self.assertEqual("2020-02-01", str(response.reservation.checkout))
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

        self.assertEqual("Hotel Foo", hotel_bookings[0].hotel_name)
        self.assertEqual(self.provider.id, hotel_bookings[0].provider_id)
        self.assertEqual("ABC123", hotel_bookings[0].simplenight_hotel_id)
        self.assertEqual("100", hotel_bookings[0].provider_hotel_id)
        self.assertIsNotNone("foo", hotel_bookings[0].record_locator)
        self.assertEqual(decimal.Decimal("120.00"), hotel_bookings[0].total_price)
        self.assertEqual("USD", hotel_bookings[0].currency)

    def test_stub_booking_with_invalid_payment(self):
        invalid_card_number_payment = test_objects.payment("4000000000000002")
        room_rate = test_objects.room_rate("foo", "100.0", base_rate="80", tax_rate="20")
        simplenight_rate = test_objects.room_rate("sn-foo", "120", base_rate="96", tax_rate="24")
        hotel = test_objects.hotel()

        booking_request = test_objects.booking_request(
            payment_obj=invalid_card_number_payment, rate_code=simplenight_rate.code
        )

        hotel_cache_service.save_provider_rate_in_cache(
            hotel=hotel, room_rate=room_rate, simplenight_rate=simplenight_rate
        )

        with patch("stripe.Token.create") as stripe_token_mock:
            stripe_token_mock.return_value = {"id": "pt_foo"}

            with patch("stripe.Charge.create") as stripe_create_mock:
                error = {"error": {"code": "card_declined"}}
                stripe_create_mock.side_effect = CardError("card_declined", 1, 1, json_body=error)
                with pytest.raises(PaymentException) as e:
                    booking_service.book(booking_request)

        assert e.value.error_type == SubmitErrorType.PAYMENT_DECLINED

    @freeze_time("2020-10-01")
    def test_cancellation(self):
        booking, hotel_booking, traveler = self._create_booking(
            first_name="John", last_name="Simplenight", provider_hotel_id="SN123"
        )

        policy_one = HotelCancellationPolicy(
            hotel_booking=hotel_booking,
            cancellation_type=CancellationSummary.FREE_CANCELLATION.value,
            description="Free cancellation before 11/1/2020",
            begin_date=date(2020, 9, 1),
            end_date=date(2020, 11, 1),
            penalty_amount=decimal.Decimal(0),
            penalty_currency="USD",
        )

        policy_two = HotelCancellationPolicy(
            hotel_booking=hotel_booking,
            cancellation_type=CancellationSummary.FREE_CANCELLATION.value,
            description="Penalty after 11/2/2020",
            begin_date=date(2020, 11, 2),
            end_date=date(2025, 11, 1),
            penalty_amount=decimal.Decimal("100.50"),
            penalty_currency="USD",
        )

        policy_one.save()
        policy_two.save()

        self._create_provider_hotel("Hotel Foo", "SN123")

        cancel_request = CancelRequest(booking_id=str(booking.booking_id), last_name="Simplenight",)
        cancel_response = booking_service.cancel(cancel_request)

        self.assertTrue(cancel_response.is_cancellable)
        self.assertEqual(CancellationSummary.FREE_CANCELLATION, cancel_response.details.cancellation_type)
        self.assertEqual("Free cancellation before 11/1/2020", cancel_response.details.description)
        self.assertEqual(date(2020, 9, 1), cancel_response.details.begin_date)
        self.assertEqual(date(2020, 11, 1), cancel_response.details.end_date)
        self.assertEqual(decimal.Decimal(0), cancel_response.details.penalty_amount)
        self.assertEqual("USD", cancel_response.details.penalty_currency)

    @freeze_time("2020-10-01")
    def test_cancellation_non_refundable(self):
        booking, hotel_booking, traveler = self._create_booking(
            first_name="John", last_name="Simplenight", provider_hotel_id="PROVIDER123"
        )

        policy_one = HotelCancellationPolicy(
            hotel_booking=hotel_booking,
            cancellation_type=CancellationSummary.FREE_CANCELLATION.value,
            description="Free cancellation before 9/1/2020",
            begin_date=date(2015, 1, 1),
            end_date=date(2020, 9, 1),
            penalty_amount=decimal.Decimal(0),
            penalty_currency="USD",
        )

        policy_two = HotelCancellationPolicy(
            hotel_booking=hotel_booking,
            cancellation_type=CancellationSummary.NON_REFUNDABLE.value,
            description="Penalty after 11/2/2020",
            begin_date=date(2020, 9, 2),
            end_date=date(2025, 11, 1),
            penalty_amount=decimal.Decimal("100.50"),
            penalty_currency="USD",
        )

        policy_one.save()
        policy_two.save()

        self._create_provider_hotel(hotel_name="Foo Hotel", provider_code="PROVIDER123")

        cancel_request = CancelRequest(booking_id=str(booking.booking_id), last_name="Simplenight",)
        cancel_response = booking_service.cancel(cancel_request)

        self.assertFalse(cancel_response.is_cancellable)
        self.assertEqual("Hotel Foo", cancel_response.itinerary.name)
        self.assertEqual(decimal.Decimal("100.0"), cancel_response.itinerary.price.amount)
        self.assertEqual("USD", cancel_response.itinerary.price.currency)
        self.assertEqual("SN123", cancel_response.itinerary.confirmation)
        self.assertEqual("2020-01-01", str(cancel_response.itinerary.start_date))
        self.assertEqual("2020-01-07", str(cancel_response.itinerary.end_date))
        self.assertEqual("123 Main Street", cancel_response.itinerary.address.address1)
        self.assertEqual("10th Floor", cancel_response.itinerary.address.address2)
        self.assertEqual("US", cancel_response.itinerary.address.country)
        self.assertEqual("Simpleville", cancel_response.itinerary.address.city)
        self.assertEqual("94111", cancel_response.itinerary.address.postal_code)
        self.assertEqual(CancellationSummary.NON_REFUNDABLE, cancel_response.details.cancellation_type)
        self.assertEqual("Penalty after 11/2/2020", cancel_response.details.description)
        self.assertEqual("2020-09-02", str(cancel_response.details.begin_date))
        self.assertEqual("2025-11-01", str(cancel_response.details.end_date))
        self.assertEqual(decimal.Decimal("100.50"), cancel_response.details.penalty_amount)
        self.assertEqual("USD", cancel_response.details.penalty_currency)

        # Incorrect Last Name
        with pytest.raises(BookingException) as e:
            cancel_request = CancelRequest(booking_id=str(booking.booking_id), last_name="DoesNotExist")
            booking_service.cancel(cancel_request)

        self.assertIn("Could not find booking", str(e))

        # Incorrect Booking ID
        with pytest.raises(BookingException) as e:
            cancel_request = CancelRequest(booking_id=str(uuid.uuid4()), last_name="Simplenight")
            booking_service.cancel(cancel_request)

        self.assertIn("Could not find booking", str(e))

    @staticmethod
    def _create_booking(first_name, last_name, provider_hotel_id) -> Sequence:
        provider = Provider.objects.get_or_create(name="Foo")[0]
        provider.save()
        traveler = Traveler(
            first_name=first_name,
            last_name=last_name,
            email_address="john.simplenight@foo.bar",
            phone_number="5558675309",
        )
        traveler.save()
        booking = Booking(
            transaction_id="foo",
            booking_date=datetime.now(),
            booking_status=BookingStatus.BOOKED.value,
            lead_traveler=traveler,
        )
        booking.save()
        hotel_booking = HotelBooking(
            booking=booking,
            created_date=datetime.now(),
            hotel_name="Hotel Foo",
            provider=provider,
            simplenight_hotel_id="123",
            provider_hotel_id=provider_hotel_id,
            record_locator="SN123",
            total_price=decimal.Decimal("100.0"),
            currency="USD",
            provider_total=decimal.Decimal("80.0"),
            provider_currency="USD",
            checkin=date(2020, 1, 1),
            checkout=date(2020, 1, 7),
        )
        hotel_booking.save()

        return booking, hotel_booking, traveler

    @staticmethod
    def _get_payment_transaction():
        transaction = PaymentTransaction()
        transaction.provider_name = "stripe"
        transaction.currency = "USD"
        transaction.charge_id = "charge-id"
        transaction.transaction_amount = 100.0
        transaction.transaction_status = "success"
        transaction.payment_token = "pt_foo"

        return transaction

    @staticmethod
    def _create_provider_hotel(hotel_name, provider_code):
        provider_hotel = ProviderHotel(
            hotel_name=hotel_name,
            provider_code=provider_code,
            provider=Provider.objects.get_or_create(name="Foo")[0],
            city_name="Simpleville",
            state="CA",
            country_code="US",
            postal_code="94111",
            address_line_1="123 Main Street",
            address_line_2="10th Floor",
        )

        provider_hotel.save()
        return provider_hotel
