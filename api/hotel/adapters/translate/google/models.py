#######################################
#   Google Hotel Booking API Schema   #
#######################################

import dataclasses
from dataclasses import field
from datetime import date
from enum import Enum
from typing import List, Optional

import marshmallow_dataclass
from marshmallow import EXCLUDE

from api.common.models import BaseSchema, Address, Money, RoomRate, RemoveNone
from api.hotel.hotel_model import GeoLocation, BedTypes


class ApiVersion(Enum):
    VERSION_1: 1


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class DisplayString:
    text: str
    language: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class BasicAmenities:
    free_breakfast: bool
    free_wifi: bool
    free_parking: bool


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleImage(BaseSchema):
    url: str
    description: DisplayString


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomCapacity(RemoveNone):
    adults: int = 2
    children: Optional[int] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleRoomType(BaseSchema, RemoveNone):
    class Meta:
        unknown = EXCLUDE

    code: str
    name: DisplayString
    description: Optional[DisplayString]
    basic_amenities: BasicAmenities
    photos: List[GoogleImage]
    capacity: RoomCapacity
    bed_types: Optional[BedTypes] = None
    unstructured_policies: Optional[DisplayString] = None


# Room Occupancy, but Google-required format
# Children are specified as a list of integers representing child age
@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomParty(BaseSchema):
    children: List[int] = field(default_factory=list)
    adults: int = 0


class GuaranteeType(Enum):
    NO_GUARANTEE = "NO_GUARANTEE"
    PAYMENT_CARD = "PAYMENT_CARD"


class CancellationSummary(Enum):
    UNKNOWN_CANCELLATION_POLICY = "UNKNOWN_CANCELLATION_POLICY"
    FREE_CANCELLATION = "FREE_CANCELLATION"
    NON_REFUNDABLE = "NON_REFUNDABLE"
    PARTIAL_REFUND = "PARTIAL_REFUND"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleCancellationPolicy(BaseSchema):
    summary: CancellationSummary
    cancellation_deadline: str
    unstructured_policy: DisplayString


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleRatePlan(BaseSchema):
    code: str
    name: DisplayString
    description: DisplayString
    basic_amenities: BasicAmenities
    guarantee_type: GuaranteeType
    cancellation_policy: GoogleCancellationPolicy


class LineItemType(Enum):
    BASE_RATE = "BASE_RATE"
    UNKNOWN_TAXES_AND_FEES = "UNKNOWN_TAXES_AND_FEES"
    UNKNOWN_TAXES = "UNKNOWN_TAXES"
    TAX_MUNICIPAL = "TAX_MUNICIPAL"
    TAX_VAT = "TAX_VAT"
    TAX_OTHER = "TAX_OTHER"
    UNKNOWN_FEES = "UNKNOWN_FEES"
    FEE_BOOKING = "FEE_BOOKING"
    FEE_HOTEL = "FEE_HOTEL"
    FEE_RESORT = "FEE_RESORT"
    FEE_TRANSFER = "FEE_TRANSFER"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomRateLineItem(BaseSchema):
    price: Money
    type: LineItemType
    paid_at_checkout: bool


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleRoomRate(BaseSchema):
    code: str
    room_type_code: str
    rate_plan_code: str
    maximum_allowed_occupancy: RoomCapacity
    total_price_at_booking: Money
    total_price_at_checkout: Money
    line_items: List[RoomRateLineItem]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleHotelDetails(BaseSchema):
    name: str
    address: Address
    geolocation: Optional[GeoLocation] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleHotelApiResponse(BaseSchema):
    api_version: int
    transaction_id: str
    hotel_id: str
    start_date: date
    end_date: date
    party: RoomParty
    room_types: List[GoogleRoomType]
    rate_plans: List[GoogleRatePlan]
    room_rates: List[GoogleRoomRate]
    hotel_details: GoogleHotelDetails


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleHotelSearchRequest(BaseSchema):
    api_version: int
    transaction_id: str
    hotel_id: str
    start_date: date
    end_date: date
    party: RoomParty
    language: str = "en"
    currency: str = "USD"
