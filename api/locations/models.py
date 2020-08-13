import dataclasses

import marshmallow_dataclass


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class LocationResponse:
    location_id: int
    language_code: str
    location_name: str
    province_code: str
    iso_country_code: str
