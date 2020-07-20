import dataclasses
from typing import List, Optional

import marshmallow_dataclass
from dataclasses import field

from api.hotel.adapters.hotelbeds.common import HotelBedsAuditDataRS, HotelBedsCoordinates
from api.hotel.hotel_model import BaseSchema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsContent(BaseSchema):
    content: str
    street: Optional[str]
    number: Optional[str]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsPhone(BaseSchema):
    phone_number: str = field(metadata=dict(data_key="phoneNumber"))
    phone_type: str = field(metadata=dict(data_key="phoneType"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsImage(BaseSchema):
    image_type: str = field(metadata=dict(data_key="imageTypeCode"))
    path: str = field(metadata=dict(data_key="path"))
    order: int = field(metadata=dict(data_key="order"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsHotelDetail(BaseSchema):
    code: int = field(metadata=dict(data_key="code"))
    name: HotelBedsContent = field(metadata=dict(data_key="name"))
    description: HotelBedsContent = field(metadata=dict(data_key="description"))
    country_code: str = field(metadata=dict(data_key="countryCode"))
    state_code: str = field(metadata=dict(data_key="stateCode"))
    coordinates: HotelBedsCoordinates = field(metadata=dict(data_key="coordinates"))
    chain_code: Optional[str] = field(metadata=dict(data_key="chainCode"))
    accommodation_type: str = field(metadata=dict(data_key="accommodationTypeCode"))
    address: HotelBedsContent = field(metadata=dict(data_key="address"))
    postal_code: Optional[str] = field(metadata=dict(data_key="postalCode"))
    city: HotelBedsContent = field(metadata=dict(data_key="city"))
    email: Optional[str] = field(metadata=dict(data_key="email"))
    phones: List[HotelBedsPhone] = field(metadata=dict(data_key="phones"), default_factory=list)
    images: List[HotelBedsImage] = field(metadata=dict(data_key="images"), default_factory=list)


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsHotelDetailsRS(BaseSchema):
    start: int = field(metadata=dict(data_key="from"))
    end: int = field(metadata=dict(data_key="to"))
    total: int = field(metadata=dict(data_key="total"))
    audit_data: HotelBedsAuditDataRS = field(metadata=dict(data_key="auditData"))
    hotels: List[HotelBedsHotelDetail]
