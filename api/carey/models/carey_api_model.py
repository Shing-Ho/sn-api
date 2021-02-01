from decimal import Decimal
from typing import Optional

from api.common.common_models import SimplenightModel

from api.locations.models import Location


class StateProvType(SimplenightModel):
    value: str
    stateCode: str


class CountryNameType(SimplenightModel):
    value: str
    stateCode: str


class FlightInfo(SimplenightModel):
    flightDate: str
    flightNum: str
    flightCode: str


class DropOffLocation(SimplenightModel):
    latitude: Decimal
    longitude: Decimal
    locationName: str
    addressLine: Optional[str]
    cityName: Optional[str]
    postalCode: str
    stateProv: object
    countryName: Optional[CountryNameType]


class RateInquiryRequest(SimplenightModel):
    dateTime: str
    passengers: int
    bags: int
    tripType: str = "Point-To-Point"
    pickUpLoacation: Location
    flightInfo: FlightInfo
    dropOffLocation: DropOffLocation
    special: Optional[str]
