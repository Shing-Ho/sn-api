import decimal
from unittest.mock import patch

import pytest
from stripe.error import CardError

from api.booking import booking_service
from api.booking.booking_model import Payment, HotelBookingRequest, Customer, Traveler, PaymentMethod, SubmitErrorType
from api.common.models import RoomOccupancy, Address
from api.hotel import hotel_cache_service
from api.models import models
from api.models.models import Booking, BookingStatus, PaymentTransaction
from api.tests import test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.view.exceptions import PaymentException


class TestBookingService(SimplenightTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_stub_booking(self):
        booking_request = HotelBookingRequest(
            api_version=1,
            transaction_id="foo",
            hotel_id="ABC123",
            language="en_US",
            customer=Customer(
                first_name="John", last_name="Doe", phone_number="5558675309", email="john@doe.foo", country="US"
            ),
            traveler=Traveler(first_name="John", last_name="Doe", occupancy=RoomOccupancy(adults=1)),
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

        self.assertEqual("Hotel Name", hotel_bookings[0].hotel_name)
        self.assertEqual("stub", hotel_bookings[0].provider_name)
        self.assertEqual("ABC123", hotel_bookings[0].hotel_code)
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
