import dataclasses
import decimal
from dataclasses import field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

import marshmallow_dataclass
from marshmallow import EXCLUDE

from api.common.models import BaseSchema, RemoveNone, RoomOccupancy, Address, HotelRate, RoomRate


class SimplenightAmenities(Enum):
    POOL = "Pool"
    FREE_PARKING = "Free Parking"
    PARKING = "Parking"
    BREAKFAST = "Breakfast"
    WIFI = "Free Wi-Fi"
    AIRPORT_SHUTTLE = "Free Airport Shuttle"
    KITCHEN = "Kitchen"
    PET_FRIENDLY = "Pet Friendly"
    AIR_CONDITIONING = "Air Conditioned"
    CASINO = "Casino"
    WATER_PARK = "Water Park"
    ALL_INCLUSIVE = "All Inclusive"
    SPA = "Spa"
    WASHER_DRYER = "Washer and Dryer"
    LAUNDRY_SERVICES = "Laundry Services"
    HOT_TUB = "Hot Tub"
    BAR = "Bar"
    MINIBAR = "Mini Bar"
    GYM = "Health Club or Gym"
    RESTAURANT = "Restaurant"
    SAUNA = "Sauna"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class BaseHotelSearch(BaseSchema, RemoveNone):
    start_date: date
    end_date: date
    occupancy: Optional[RoomOccupancy]
    daily_rates: bool = False
    language: Optional[str] = "en"
    currency: Optional[str] = "USD"
    checkin_time: Optional[Union[str, datetime]] = None
    checkout_time: Optional[Union[str, datetime]] = None
    crs: str = "stub"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelLocationSearch(BaseHotelSearch):
    location_name: str = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelSpecificSearch(BaseHotelSearch):
    hotel_id: str = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelDetailsSearchRequest(BaseSchema):
    hotel_code: str
    start_date: date
    end_date: date
    num_rooms: int = 1
    currency: str = "USD"
    language: str = "en_US"
    crs: str = "stub"
    chain_code: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelAdapterHotel(BaseSchema):
    name: str
    address: Address
    rate: HotelRate
    chain_code: Optional[str]
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
    description: Optional[str]
    amenities: List[SimplenightAmenities]
    photos: List[Image]
    capacity: RoomOccupancy
    bed_types: Optional[BedTypes]
    unstructured_policies: Optional[str] = None


class CancellationSummary(Enum):
    UNKNOWN_CANCELLATION_POLICY = "UNKNOWN_CANCELLATION_POLICY"
    FREE_CANCELLATION = "FREE_CANCELLATION"
    NON_REFUNDABLE = "NON_REFUNDABLE"
    PARTIAL_REFUND = "PARTIAL_REFUND"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class CancellationPolicy(BaseSchema):
    summary: CancellationSummary
    cancellation_deadline: Optional[date] = None
    unstructured_policy: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RatePlan(BaseSchema):
    code: str
    name: str
    description: str
    amenities: List[SimplenightAmenities]
    cancellation_policy: CancellationPolicy


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
    hotel_code: str
    checkin_time: Optional[str]
    checkout_time: Optional[str]
    photos: List[Image] = field(default_factory=list)
    amenities: Optional[List[SimplenightAmenities]] = field(default_factory=list)
    geolocation: Optional[GeoLocation] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    homepage_url: Optional[str] = None
    chain_code: Optional[str] = None
    star_rating: Optional[float] = None
    property_description: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class ErrorResponse(BaseSchema):
    type: str
    message: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class CrsHotel(BaseSchema):
    crs: str
    hotel_id: str
    start_date: date
    end_date: date
    occupancy: RoomOccupancy
    room_types: List[RoomType]
    rate_plans: Optional[List[RatePlan]] = None
    room_rates: Optional[List[RoomRate]] = None
    hotel_details: Optional[HotelDetails] = None
    error: Optional[ErrorResponse] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Hotel(BaseSchema):
    hotel_id: str
    start_date: date
    end_date: date
    occupancy: RoomOccupancy
    hotel_details: Optional[HotelDetails]
    room_types: Optional[List[RoomType]] = None
    room_rates: Optional[List[RoomRate]] = None
    rate_plans: Optional[List[RatePlan]] = None
    average_nightly_rate: decimal.Decimal = field(metadata=dict(as_string=True), default=None)
    average_nightly_base: decimal.Decimal = field(metadata=dict(as_string=True), default=None)
    average_nightly_tax: decimal.Decimal = field(metadata=dict(as_string=True), default=None)
    error: Optional[ErrorResponse] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelPriceVerification(BaseSchema):
    is_allowed_change: bool
    is_exact_price: bool
    room_rates: List[RoomRate]
    original_total: decimal.Decimal = field(metadata=dict(as_string=True))
    recheck_total: decimal.Decimal = field(metadata=dict(as_string=True))
    price_difference: decimal.Decimal = field(metadata=dict(as_string=True))
