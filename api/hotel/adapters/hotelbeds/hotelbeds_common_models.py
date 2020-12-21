from enum import Enum


HOTELBEDS_LANGUAGE_MAP = {
    "en": "ENG",
}

def get_language_mapping(language):
    return HOTELBEDS_LANGUAGE_MAP.get(language, "ENG")

class HotelbedsRateType(Enum):
    BOOKABLE = "BOOKABLE"
    RECHECK = "RECHECK"

class HotelbedsPaymentType(Enum):
    AT_HOTEL = "AT_HOTEL"
    AT_WEB = "AT_WEB"
