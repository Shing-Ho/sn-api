import decimal
import json
from datetime import date
from enum import Enum
from typing import Optional, List, Union, TypeVar, Type

from pydantic.main import BaseModel


class SimplenightModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class RoomOccupancy(SimplenightModel):
    adults: Optional[int] = 1
    children: Optional[int] = 0
    num_rooms: Optional[int] = 1


class Address(SimplenightModel):
    city: str
    province: str
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


T = TypeVar("T")


def from_json(obj, cls: Type[T], many=False) -> Union[List[T], T]:
    if many:
        return list(map(cls.parse_obj, json.loads(obj)))

    if isinstance(obj, str):
        return cls.parse_raw(obj)

    return cls.parse_obj(obj)


def to_json(obj: Union[SimplenightModel, List[SimplenightModel]], many=False, indent=2):
    class ItemList(SimplenightModel):
        __root__: List[SimplenightModel]

    if many:
        return ItemList.parse_obj(obj).json(indent=indent)

    return obj.json(indent=indent)
