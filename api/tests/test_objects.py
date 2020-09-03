import decimal
import uuid
from datetime import date, timedelta, datetime

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
from api.hotel.hotel_model import CrsHotel, RoomType, HotelSpecificSearch
from api.tests import to_money


def hotel(room_rates=None):
    if room_rates is None:
        room_rates = []

    return CrsHotel(
        crs="stub",
        hotel_id="100",
        start_date=date(2020, 1, 1),
        end_date=date(2020, 2, 1),
        occupancy=RoomOccupancy(adults=1),
        room_rates=room_rates,
        room_types=[],
        rate_plans=[],
        hotel_details=None,
    )


def room_rate(rate_key: str, total, base_rate=None, tax_rate=None):
    if isinstance(total, str):
        total = to_money(total)

    if base_rate is None:
        base_rate = total.amount * decimal.Decimal("0.85")

    if tax_rate is None:
        tax_rate = total.amount * decimal.Decimal("0.15")

    return RoomRate(
        code=rate_key,
        rate_plan_code="foo",
        room_type_code="foo",
        rate_type=RateType.BOOKABLE,
        total_base_rate=to_money(base_rate),
        total_tax_rate=to_money(tax_rate),
        total=total,
        maximum_allowed_occupancy=RoomOccupancy(adults=2),
    )


def room_type():
    return RoomType(
        code=str(uuid.uuid4),
        name=f"Test Rate {str(uuid.uuid4())[:4]}",
        description="Test Description",
        amenities=[],
        photos=[],
        capacity=RoomOccupancy(adults=2),
        bed_types=None,
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


def booking_request(payment_obj=None, rate=None):
    if payment_obj is None:
        payment_obj = payment(card_number="4242424242424242")

    if rate is None:
        rate = room_rate("rate_key", "1.00")

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
        room_rates=[rate],
        payment=payment_obj,
    )


def hotel_specific_search(start_date=None, end_date=None, hotel_id="123", adapter="stub"):
    if start_date is None:
        start_date = date(2020, 1, 1)

    if end_date is None:
        end_date = date(2020, 1, 7)

    return HotelSpecificSearch(
        start_date=start_date,
        end_date=end_date,
        occupancy=RoomOccupancy(),
        daily_rates=False,
        hotel_id=hotel_id,
        crs=adapter,
    )
