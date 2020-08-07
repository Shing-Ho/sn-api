import decimal
import uuid
from datetime import date, timedelta, datetime
from typing import Union

from api.booking.booking_model import (
    Customer,
    Traveler,
    Payment,
    PaymentCardParameters,
    CardType,
    PaymentMethod,
    HotelBookingRequest,
)
from api.common.models import RoomRate, RateType, RoomOccupancy, Address
from api.hotel.hotel_model import Hotel
from api.tests import to_money


def hotel():
    return Hotel(
        crs="stub",
        hotel_id="100",
        start_date=date(2020, 1, 1),
        end_date=date(2020, 2, 1),
        occupancy=RoomOccupancy(adults=1),
        room_types=[],
        hotel_details=None,
    )


def room_rate(rate_key: str, amount: Union[decimal.Decimal, str]):
    return RoomRate(
        rate_key=rate_key,
        rate_type=RateType.BOOKABLE,
        description="Test Room Rate",
        additional_detail=[],
        total_base_rate=to_money("0"),
        total_tax_rate=to_money("0"),
        total=to_money(amount),
    )


def customer(first_name="John", last_name="Simp"):
    return Customer(
        first_name=first_name,
        last_name=last_name,
        phone_number="5558675309",
        email="john.simp@simplenight.com",
        country="US",
    )


def address():
    return Address(address1="123 Market St", city="San Francisco", province="CA", country="US", postal_code="94111")


def traveler(first_name="John", last_name="Simpnight"):
    return Traveler(first_name=first_name, last_name=last_name, occupancy=RoomOccupancy(adults=1, children=0))


def payment(card_number=None):
    if card_number is None:
        card_number = "4242424242424242"

    exp_date = datetime.now().date() + timedelta(days=365)
    return Payment(
        billing_address=address(),
        payment_method=PaymentMethod.PAYMENT_CARD,
        payment_card_parameters=PaymentCardParameters(
            card_type=CardType.VI,
            card_number=card_number,
            cardholder_name="John Q. Simpnight",
            expiration_month=str(exp_date.month),
            expiration_year=str(exp_date.year),
            cvv="123",
        ),
    )


def booking_request(payment_obj=None):
    if payment_obj is None:
        payment_obj = payment("4242424242424242")

    checkin = datetime.now().date() + timedelta(days=5)
    checkout = datetime.now().date() + timedelta(days=7)

    return HotelBookingRequest(
        api_version=1,
        transaction_id=str(uuid.uuid4()),
        hotel_id="1",
        checkin=checkin,
        checkout=checkout,
        language="en_US",
        customer=customer(),
        traveler=traveler(),
        room_rates=[room_rate("rate_key", "1.00")],
        payment=payment_obj,
    )
