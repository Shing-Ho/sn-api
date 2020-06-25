import dataclasses
from dataclasses import field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, ClassVar, Type

import marshmallow_dataclass
from marshmallow import Schema, EXCLUDE


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class BaseSchema(Schema):
    class Meta:
        ordered = True
        unknown = EXCLUDE


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomOccupancy(BaseSchema):
    adults: int
    children: int


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelSpecificSearch(BaseSchema):
    hotel_id: str
    checkin_date: date
    checkout_date: date
    occupancy: RoomOccupancy
    language: Optional[str] = "en"
    currency: Optional[str] = "USD"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelLocationSearch(BaseSchema):
    location_name: str
    checkin_date: date
    checkout_date: date
    num_rooms: int = 1
    num_adults: int = 1
    num_children: int = 0
    checkin_time: str = None
    checkout_time: str = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelDetailsSearchRequest(BaseSchema):
    chain_code: str
    hotel_code: str
    checkin_date: date
    checkout_date: date
    num_rooms: int = 1
    currency: str = "USD"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Address(BaseSchema):
    city: str
    province: str
    postal_code: str
    country: str
    address1: str
    address2: Optional[str] = None
    address3: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelRate(BaseSchema):
    total_price: float
    taxes: float


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Phone(BaseSchema):
    type: str
    number: str
    extension: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelAdapterHotel(BaseSchema):
    name: str
    chain_code: str
    address: Address
    rate: HotelRate
    star_rating: Optional[int] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelCommission(BaseSchema):
    has_commission: bool
    percent: int
    amount: int = 0


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RateCancelInfo(BaseSchema):
    refundable: bool


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Money(BaseSchema):
    amount: float
    currency: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class DailyRate(BaseSchema):
    rate_date: date
    base_rate: Money
    tax: Money
    total: Money


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomRate(BaseSchema):
    description: str
    additional_detail: List[str]
    rate_plan_type: str
    total_base_rate: Money
    total_tax_rate: Money
    total: Money
    daily_rates: Optional[List[DailyRate]] = field(default_factory=list)


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Amenity(Enum):
    FREE_WIFI = "Free Wifi"
    FREE_PARKING = "Free Parking"
    FREE_BREAKFAST = "Free Breakfast"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class ImageType(Enum):
    EXTERIOR = "Exterior"
    ROOM = "Room"
    UNKNOWN = ""


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Image(BaseSchema):
    url: str
    type: ImageType


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class BedTypes(BaseSchema):
    total: int = 0
    king: int = 0
    queen: int = 0
    double: int = 0
    single: int = 0
    sofa: int = 0
    murphy: int = 0
    bunk: int = 0
    other: int = 0


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomType(BaseSchema):
    class Meta:
        unknown = EXCLUDE

    code: str
    name: str
    description: str
    amenities: List[Amenity]
    photos: List[Image]
    capacity: RoomOccupancy
    bed_types: BedTypes
    unstructured_policies: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class CancellationPolicy(BaseSchema):
    summary: str
    deadline: datetime
    unstructured_policy: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RatePlan(BaseSchema):
    code: str
    name: str
    description: str
    basic_amenities: List[Amenity]
    cancellation_policy: CancellationPolicy


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomRateResponse(BaseSchema):
    code: str
    room_type_code: str
    rate_plat_code: str
    maximum_allowable_occupancy: RoomOccupancy
    total_price_at_booking: Money
    total_price_at_checkout: Money
    cancellation_rules: List[CancellationPolicy]
    unstructured_policies: List[str]
    room_count: int


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GeoLocation(BaseSchema):
    latitude: float
    longitude: float


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelDetails(BaseSchema):
    name: str
    address: Address
    chain_code: str
    hotel_code: str
    checkin_time: str
    checkout_time: str
    hotel_rates: List[RoomRate]
    geolocation: GeoLocation
    photos: List[Image] = field(default_factory=list)
    phone_number: Optional[str] = None
    email: Optional[str] = None
    homepage_url: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class ErrorResponse(BaseSchema):
    type: str
    message: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelSearchResponse(BaseSchema):
    hotel_id: str
    checkin_date: date
    checkout_date: date
    occupancy: RoomOccupancy
    room_types: List[RoomType]
    rate_plans: List[RatePlan]
    room_rates: List[RoomRate]
    hotel_details: HotelDetails
    error: Optional[ErrorResponse] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Customer(BaseSchema):
    first_name: str
    last_name: str
    phone_number: str
    email: str
    country: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Traveler(BaseSchema):
    first_name: str
    last_name: str
    occupancy: RoomOccupancy


class CardType(Enum):
    AX = "American Express"
    DC = "Diner's Club"
    DS = "Discovery"
    JC = "JCB"
    MC = "Mastercard"
    VI = "Visa"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class PaymentCardParameters(BaseSchema):
    card_type: CardType
    card_number: str
    cardholder_name: str
    expiration_month: str
    expiration_year: str
    cvv: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Payment(BaseSchema):
    payment_card_parameters: PaymentCardParameters
    billing_address: Address


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBookingRequest(BaseSchema):
    api_version: int
    transaction_id: str
    hotel_id: str
    checkin: date
    checkout: date
    language: str
    customer: Customer
    traveler: Traveler
    room_rate: RoomRate
    payment: Payment
    tracking: Optional[str] = None
    ip_address: Optional[str] = None

    Schema: ClassVar[Type[Schema]] = Schema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Status(BaseSchema):
    success: bool
    message: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Locator(BaseSchema):
    id: str
    pin: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Reservation(BaseSchema):
    locator: Locator
    hotel_locator: Locator
    hotel_id: str
    checkin: date
    checkout: date
    customer: Customer
    traveler: Traveler
    room_rate: RoomRate


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBookingResponse(BaseSchema):
    api_version: int
    transaction_id: str
    status: Status
    reservation: Reservation

    Schema: ClassVar[Type[Schema]] = Schema
