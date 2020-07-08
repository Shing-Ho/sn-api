import dataclasses
from typing import List, Optional

import marshmallow_dataclass

from api.hotel.hotels import BaseSchema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingLeadTraveler:
    name: str
    surname: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsPax:
    roomId: int
    type: str
    name: str
    surname: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingRoom:
    rateKey: str
    pax: List[HotelBedsPax]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingRQ(BaseSchema):
    holder: HotelBedsBookingLeadTraveler
    paxes: List[HotelBedsPax]
    clientReference: str
    language: Optional[str]
    rooms: List[HotelBedsBookingRoom]
    remark: Optional[str] = None
