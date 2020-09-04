import dataclasses
from decimal import Decimal
from enum import Enum
from typing import Optional

import marshmallow_dataclass


class LocationType(Enum):
    AIRPORT = "AIRPORT"
    CITY = "CITY"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass(frozen=True)
class LocationResponse:
    class Meta:
        ordered = True

    location_id: str
    language_code: str
    location_name: str
    province: Optional[str]
    iso_country_code: str
    latitude: Decimal
    longitude: Decimal
    location_type: LocationType
