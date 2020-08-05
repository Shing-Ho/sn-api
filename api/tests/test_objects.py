import decimal
from datetime import date
from typing import Union

from api.booking.booking_model import Customer, Traveler
from api.common.models import RoomRate, RateType, RoomOccupancy
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
        country="USA",
    )


def traveler(first_name="John", last_name="Simp"):
    return Traveler(first_name=first_name, last_name=last_name, occupancy=RoomOccupancy(adults=1, children=0))
