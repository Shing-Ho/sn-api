import dataclasses
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Optional, List

import marshmallow_dataclass

from api.hotel.hotels import BaseSchema

HOTELBEDS_LANGUAGE_MAP = {
    "en_US": "ENG",
}


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsAuditDataRS(BaseSchema):
    timestamp: datetime
    environment: str
    release: str
    process_time: str = field(metadata=dict(data_key="processTime"))
    request_host: str = field(metadata=dict(data_key="requestHost"))
    server_id: str = field(metadata=dict(data_key="serverId"))


class HotelBedsRateType(Enum):
    BOOKABLE = "BOOKABLE"
    RECHECK = "RECHECK"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsCoordinates(BaseSchema):
    latitude: float
    longitude: float


class HotelBedsTaxType(Enum):
    TAX = "TAX"
    FEE = "FEE"
    TAXESANDFEE = "TAXESANDFEE"


class HotelBedsPaymentType(Enum):
    AT_HOTEL = "AT_HOTEL"
    AT_WEB = "AT_WEB"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsCancellationPoliciesRS(BaseSchema):
    deadline: datetime = field(metadata=dict(data_key="from"))
    amount: str = field(metadata=dict(data_key="amount"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsPromotionsRS(BaseSchema):
    code: str
    name: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsTaxRS(BaseSchema):
    included: bool
    amount: str
    currency: str
    type: Optional[HotelBedsTaxType]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsTaxesRS(BaseSchema):
    taxes: List[HotelBedsTaxRS] = field(metadata=dict(data_key="taxes"))
    all_included: bool = field(metadata=dict(data_key="allIncluded"))


def get_language_mapping(language):
    return HOTELBEDS_LANGUAGE_MAP.get(language, "ENG")
