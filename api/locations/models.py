from decimal import Decimal
from enum import Enum
from typing import Optional

from api.common.models import SimplenightModel


class LocationType(Enum):
    AIRPORT = "AIRPORT"
    CITY = "CITY"


class LocationResponse(SimplenightModel):
    # Make LocationResponse hashable
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))

    location_id: str
    language_code: str
    location_name: str
    province: Optional[str]
    iso_country_code: str
    latitude: Decimal
    longitude: Decimal
    location_type: LocationType
