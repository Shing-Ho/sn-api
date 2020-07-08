import dataclasses
from dataclasses import field
from datetime import datetime

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


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsCoordinates(BaseSchema):
    latitude: float
    longitude: float


def get_language_mapping(language):
    return HOTELBEDS_LANGUAGE_MAP.get(language, "ENG")
