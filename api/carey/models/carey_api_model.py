from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from api.common.common_models import SimplenightModel


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


class Location(SimplenightModel):
    latitude: Decimal
    longitude: Decimal
    locationName: str
    addressLine: Optional[str]
    cityName: Optional[str]
    postalCode: str
    stateProv: object
    countryName: Optional[CountryNameType]
    airport: Optional[bool]
    airportCode: Optional[str]
    trainStation: Optional[bool]


class RateInquiryRequest(SimplenightModel):
    dateTime: str
    passengers: int
    bags: int
    tripType: str = "Point-To-Point"
    pickUpLoacation: Location
    flightInfo: Optional[FlightInfo]
    dropOffLocation: Location
    special: Optional[str]


class VehicleDetails(SimplenightModel):
    vehicleName: str
    vehicleCode: str
    vehicleDescriptionDetail: str
    maxPassengers: int
    maxBags: int


class Reference(SimplenightModel):
    estimatedDistance: str
    estimatedTime: str


class ChargeDetails(SimplenightModel):
    readBack: str
    billingType: str


class ChargeItem(SimplenightModel):
    itemName: str
    itemDescription: str
    itemUnit: str
    itemUnitValue: Decimal
    itemUnitPrice: Decimal
    itemUnitPriceCurrency: str
    readBack: str
    sequenceNumber: int


class TotalAmount(SimplenightModel):
    totalAmountValue: Decimal
    totalAmountCurrency: str
    totalAmountDescription: str


class AdditionalInfo(SimplenightModel):
    notice: str
    garageToGarageEstimate: str


class QuoteResponse(SimplenightModel):
    pickUpDate: datetime
    pickUpLoacation: Location
    dropOffLocation: Location
    vehicleDetails: VehicleDetails
    chargeDetails: ChargeDetails
    chargeItems: List[ChargeItem]
    reference: Reference
    total: TotalAmount
    additional: AdditionalInfo
    special: Optional[str]
