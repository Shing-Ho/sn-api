import dataclasses
from decimal import Decimal

import marshmallow_dataclass


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class LocationResponse:
    class Meta:
        ordered = True

    location_id: int
    language_code: str
    location_name: str
    province_code: str
    iso_country_code: str
    latitude: Decimal
    longitude: Decimal
