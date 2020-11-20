import decimal
from datetime import date
from enum import Enum
from typing import Optional, List

from api.common.common_models import SimplenightModel


class RoomOccupancy(SimplenightModel):
    adults: Optional[int] = 1
    children: Optional[int] = 0
    num_rooms: Optional[int] = 1


class Address(SimplenightModel):
    city: str
    province: Optional[str] = None
    country: str
    address1: str
    address2: Optional[str] = None
    address3: Optional[str] = None
    postal_code: Optional[str] = None


class HotelRate(SimplenightModel):
    total_price: float
    taxes: float


class Phone(SimplenightModel):
    type: str
    number: str
    extension: str


class RateType(Enum):
    RECHECK = "RECHECK"
    BOOKABLE = "BOOKABLE"


class Money(SimplenightModel):
    amount: decimal.Decimal
    currency: str


class DailyRate(SimplenightModel):
    rate_date: date
    base_rate: Money
    tax: Money
    total: Money


class LineItemType(Enum):
    BASE_RATE = "BASE_RATE"
    UNKNOWN_TAXES_AND_FEES = "UNKNOWN_TAXES_AND_FEES"
    UNKNOWN_TAXES = "UNKNOWN_TAXES"
    TAX_MUNICIPAL = "TAX_MUNICIPAL"
    TAX_VAT = "TAX_VAT"
    TAX_OTHER = "TAX_OTHER"
    UNKNOWN_FEES = "UNKNOWN_FEES"
    FEE_BOOKING = "FEE_BOOKING"
    FEE_HOTEL = "FEE_HOTEL"
    FEE_RESORT = "FEE_RESORT"
    FEE_TRANSFER = "FEE_TRANSFER"


class PostpaidFeeLineItem(SimplenightModel):
    amount: Money
    type: LineItemType
    description: str


class PostpaidFees(SimplenightModel):
    total: Money
    fees: List[PostpaidFeeLineItem]


class RoomRate(SimplenightModel):
    code: str
    room_type_code: str
    rate_plan_code: str
    maximum_allowed_occupancy: RoomOccupancy
    total_base_rate: Money
    total_tax_rate: Money
    total: Money
    rate_type: RateType
    daily_rates: Optional[List[DailyRate]] = None
    postpaid_fees: Optional[PostpaidFees] = None
    partner_data: Optional[List[str]] = None


class BookingStatus(Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    PENDING = "pending"

    @classmethod
    def from_value(cls, value):
        if not hasattr(cls, "value_map"):
            cls.value_map = {x.value: x for x in BookingStatus}

        return cls.value_map[value]