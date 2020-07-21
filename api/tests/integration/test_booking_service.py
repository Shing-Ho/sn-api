import unittest
from datetime import date

import pytest

from api.booking import booking_service
from api.booking.booking_model import Payment, HotelBookingRequest, Customer, Traveler, PaymentMethod
from api.common.models import RoomOccupancy, RoomRate, Money, RateType, Address
from api.hotel.adapters.stub.stub import StubHotelAdapter


class TestBookingService(unittest.TestCase):
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

    def test_hotelbeds_booking(self):
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
            room_rate=RoomRate(
                "foo-rate-key",
                RateType.BOOKABLE,
                description="Room Booking",
                additional_detail=[],
                total_base_rate=Money(100.99, "USD"),
                total_tax_rate=Money(20.00, "USD"),
                total=Money(120.99, "USD"),
                daily_rates=[],
            ),
            payment=Payment(
                billing_address=Address(
                    city="San Francisco", province="CA", postal_code="94111", country="US", address1="One Market Street"
                ),
                payment_method=PaymentMethod.PAYMENT_TOKEN,
                payment_token="token_foo",
            ),
            crs=StubHotelAdapter.CRS_NAME,
        )

        response = booking_service.book(booking_request)
