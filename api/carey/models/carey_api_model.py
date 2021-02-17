from decimal import Decimal
from typing import Optional, List
from api.common.common_models import SimplenightModel


class StateProvType(SimplenightModel):
    value: str
    stateCode: str


class CountryNameType(SimplenightModel):
    value: Optional[str]
    stateCode: Optional[str]


class FlightInfo(SimplenightModel):
    flightDate: str
    flightNum: str
    flightCode: str


class Location(SimplenightModel):
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    locationName: Optional[str]
    addressLine: Optional[str]
    cityName: Optional[str]
    postalCode: Optional[str]
    stateProv: Optional[CountryNameType]
    countryName: Optional[CountryNameType]
    airport: Optional[bool]
    airportCode: Optional[str]
    trainStation: Optional[bool]


class RateInquiryRequest(SimplenightModel):
    dateTime: str
    passengers: int
    bags: int
    tripType: Optional[str] = "Point-To-Point"
    pickUpLoacation: Location
    flightInfo: Optional[FlightInfo]
    dropOffLocation: Location
    special: Optional[str]


class VehicleDetails(SimplenightModel):
    vehicleName: Optional[str]
    vehicleCode: Optional[str]
    vehicleDescriptionDetail: Optional[str]
    maxPassengers: Optional[str]
    maxBags: Optional[str]


class Reference(SimplenightModel):
    estimatedDistance: Optional[str]
    estimatedTime: Optional[str]


class ChargeDetails(SimplenightModel):
    readBack: Optional[str]
    billingType: Optional[str]


class ChargeItem(SimplenightModel):
    itemName: Optional[str]
    itemDescription: Optional[str]
    itemUnit: Optional[str]
    itemUnitValue: Optional[Decimal]
    itemUnitPrice: Optional[Decimal]
    itemUnitPriceCurrency: Optional[str]
    readBack: Optional[str]
    sequenceNumber: Optional[str]


class TotalAmount(SimplenightModel):
    totalAmountValue: Decimal
    totalAmountCurrency: Optional[str]
    totalAmountDescription: Optional[str]


class AdditionalInfo(SimplenightModel):
    notice: Optional[str]
    garageToGarageEstimate: Optional[str]


class QuoteResponse(SimplenightModel):
    pickUpDate: str
    pickUpLoacation: Location
    dropOffLocation: Location
    flightInfo: Optional[FlightInfo]
    vehicleDetails: VehicleDetails
    chargeDetails: ChargeDetails
    chargeItems: List[ChargeItem]
    reference: Reference
    total: TotalAmount
    additional: AdditionalInfo
    special: Optional[str]
    tripType: str = "Point-To-Point"
    passengers: int
    bags: int


class PassengerInfo(SimplenightModel):
    firstName: str
    lastName: str
    phoneNum: str
    email: str


class PaymentInfo(SimplenightModel):
    cardType: str
    cardNum: str
    cardName: str
    expCVV: str
    expDate: str
    billingAddress: Location


class BookReservationRequest(SimplenightModel):
    passengerInfo: PassengerInfo
    paymentInfo: PaymentInfo
    quoteInfo: QuoteResponse


class NameType(SimplenightModel):
    firstName: Optional[str]
    lastName: Optional[str]


class TotalChargeType(SimplenightModel):
    total: Optional[str]
    currency: Optional[str]


class Airport(SimplenightModel):
    airportName: Optional[str]
    airportCode: Optional[str]


class Airline(SimplenightModel):
    countryCode: Optional[str]
    FlightNumber: Optional[str]
    FlightDateTime: Optional[str]


class BookingResponseLocation(SimplenightModel):
    address: Optional[Location]
    airport: Optional[Airport]
    airline: Optional[Airline]


class BookResponse(SimplenightModel):
    confirm_id: str
    email: Optional[str]
    name: Optional[NameType]
    pickupDate: str
    pickUpLocation: BookingResponseLocation
    dropOffLocation: BookingResponseLocation
    total: Optional[TotalChargeType]
    sequenceNmbr: Optional[str]
    version: Optional[Decimal]


class FindReservationRequest(SimplenightModel):
    reservation_id: str
    lastName: str


class CancelReservationRequest(SimplenightModel):
    reservation_id: str
    sequenceNmbr: str
    email: str
    version: Decimal


class CancelResponse(SimplenightModel):
    cancel_id: str
    reservation_id: str
    name: Optional[NameType]
    pickUpdate: str
    pickUpLocation: BookingResponseLocation
