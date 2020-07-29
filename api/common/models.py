import dataclasses
import decimal
from dataclasses import field
from datetime import date
from enum import Enum
from typing import Optional, List, Dict, Any, TypeVar, Type

import marshmallow_dataclass
from marshmallow import EXCLUDE, post_dump


class BaseSchema:
    class Meta:
        ordered = True
        unknown = EXCLUDE


def to_json(obj):
    return obj.Schema().dump(obj)


def to_jsons(obj):
    return obj.Schema().dumps(obj)


T = TypeVar("T")


def from_json(obj: Dict[Any, Any], cls: Type[T]) -> T:
    return cls.Schema().load(obj)


def from_jsons(obj: Dict[Any, Any], cls: Type[T]) -> T:
    return cls.Schema().loads(obj)


# noinspection PyUnusedLocal
class RemoveNone:
    @post_dump
    def remove_nones(self, data, **kwargs):
        none_keys = [key for key, value in data.items() if value is None]
        for key in none_keys:
            data.pop(key)
        return data


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomOccupancy(BaseSchema):
    adults: Optional[int] = 1
    children: Optional[int] = 0
    num_rooms: Optional[int] = 1


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Address(BaseSchema):
    city: str
    province: str
    country: str
    address1: str
    address2: Optional[str] = None
    address3: Optional[str] = None
    postal_code: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelRate(BaseSchema):
    total_price: float
    taxes: float


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Phone(BaseSchema):
    type: str
    number: str
    extension: str


class RateType(Enum):
    RECHECK = "RECHECK"
    BOOKABLE = "BOOKABLE"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Money(BaseSchema):
    amount: decimal.Decimal = field(metadata=dict(as_string=True))
    currency: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class DailyRate(BaseSchema):
    rate_date: date
    base_rate: Money
    tax: Money
    total: Money


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomRate(BaseSchema):
    rate_key: str
    rate_type: RateType
    description: str
    additional_detail: List[str]
    total_base_rate: Money
    total_tax_rate: Money
    total: Money
    daily_rates: Optional[List[DailyRate]] = field(default_factory=list)
