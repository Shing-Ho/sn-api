import decimal
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import Field

from api.common.models import SimplenightModel
from api.hotel.models.hotel_api_model import SimplenightAmenities

HOTELBEDS_LANGUAGE_MAP = {
    "en_US": "ENG",
}


class HotelBedsException(Exception):
    pass


class HotelBedsAuditDataRS(SimplenightModel):
    timestamp: datetime
    environment: str
    release: str
    process_time: str = Field(alias="processTime")
    request_host: str = Field(alias="requestHost")
    server_id: str = Field(alias="serverId")


class HotelBedsRateType(Enum):
    BOOKABLE = "BOOKABLE"
    RECHECK = "RECHECK"


class HotelBedsCoordinates(SimplenightModel):
    latitude: float
    longitude: float


class HotelBedsTaxType(Enum):
    TAX = "TAX"
    FEE = "FEE"
    TAXESANDFEE = "TAXESANDFEE"


class HotelBedsPaymentType(Enum):
    AT_HOTEL = "AT_HOTEL"
    AT_WEB = "AT_WEB"


class HotelBedsCancellationPoliciesRS(SimplenightModel):
    deadline: datetime = Field(alias="from")
    amount: str = Field(alias="amount")


class HotelBedsPromotionsRS(SimplenightModel):
    code: str
    name: str


class HotelBedsTaxRS(SimplenightModel):
    included: bool
    amount: Optional[decimal.Decimal]
    currency: Optional[str]
    type: Optional[HotelBedsTaxType]


class HotelBedsTaxesRS(SimplenightModel):
    taxes: List[HotelBedsTaxRS] = Field(alias="taxes")
    all_included: bool = Field(alias="allIncluded")


def get_language_mapping(language):
    return HOTELBEDS_LANGUAGE_MAP.get(language, "ENG")


HOTELBEDS_AMENITY_MAPPING = {
    SimplenightAmenities.POOL: [306, 313, 326, 360, 361, 362, 363, 364, 365, 573],
    SimplenightAmenities.FREE_PARKING: [],
    SimplenightAmenities.PARKING: [500, 560, 320],
    SimplenightAmenities.BREAKFAST: [40, 11, 12, 160, 170, 180, 264, 30, 35, 36],
    SimplenightAmenities.WIFI: [100],
    SimplenightAmenities.AIRPORT_SHUTTLE: [562],
    SimplenightAmenities.KITCHEN: [110, 115],
    SimplenightAmenities.PET_FRIENDLY: [535, 540],
    SimplenightAmenities.AIR_CONDITIONING: [170, 180],
    SimplenightAmenities.CASINO: [180],
    SimplenightAmenities.WATER_PARK: [610],
    SimplenightAmenities.ALL_INCLUSIVE: [259],
    SimplenightAmenities.SPA: [460, 620],
    SimplenightAmenities.WASHER_DRYER: [145, 321, 568],
    SimplenightAmenities.LAUNDRY_SERVICES: [280],
    SimplenightAmenities.HOT_TUB: [305, 410],
    SimplenightAmenities.BAR: [555, 570, 130],
    SimplenightAmenities.MINIBAR: [120],
    SimplenightAmenities.GYM: [470, 308, 295],
    SimplenightAmenities.RESTAURANT: [200, 840, 845],
    SimplenightAmenities.SAUNA: [307],
}
