#######################################
#   Google Hotel Booking API Schema   #
#######################################

import dataclasses
from dataclasses import field
from datetime import date
from enum import Enum
from typing import List, Optional

import marshmallow_dataclass
from marshmallow import EXCLUDE, validates_schema

from api.booking.booking_model import Customer, PaymentMethod, CardType, Locator, SubmitErrorType
from api.common.models import BaseSchema, Address, Money, RemoveNone, LineItemType
from api.hotel.hotel_api_model import GeoLocation, BedTypes, CancellationSummary


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


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class RoomRateLineItem(BaseSchema):
    price: Money
    type: LineItemType
    paid_at_checkout: bool


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class BaseGoogleRoomRate(BaseSchema):
    code: str
    room_type_code: str
    rate_plan_code: str
    maximum_allowed_occupancy: RoomCapacity
    total_price_at_booking: Optional[Money]
    total_price_at_checkout: Optional[Money]
    partner_data: Optional[List[str]]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleRoomRate(BaseGoogleRoomRate):
    line_items: List[RoomRateLineItem]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleBookingRoomRate(BaseGoogleRoomRate):
    line_items: Optional[List[RoomRateLineItem]]


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


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleTraveler(BaseSchema):
    first_name: str
    last_name: str
    occupancy: RoomParty


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GooglePaymentCardParameters(BaseSchema):
    card_type: CardType
    card_number: str
    cardholder_name: str
    expiration_month: str
    expiration_year: str
    cvc: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GooglePayment(BaseSchema):
    type: PaymentMethod
    billing_address: Address
    payment_card_parameters: Optional[GooglePaymentCardParameters] = None
    payment_token: Optional[str] = None

    # noinspection PyUnusedLocal
    @validates_schema
    def validate(self, data, *args, **kwargs):
        if data["type"] == PaymentMethod.PAYMENT_TOKEN and not data["payment_token"]:
            raise ValueError(f"Must set payment_token when payment_method is {PaymentMethod.PAYMENT_TOKEN.value}")

        payment_card_types = [PaymentMethod.CREDIT_CARD, PaymentMethod.PAYMENT_CARD]
        if data["type"] in payment_card_types and not data["payment_card_parameters"]:
            raise ValueError(
                f"Must set payment_card_parameters when payment_method is {PaymentMethod.CREDIT_CARD.value}"
            )


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleTracking:
    campaign_id: Optional[str]
    pos_url: Optional[str]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleSubmitError:
    type: SubmitErrorType
    message: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleBookingSubmitRequest(BaseSchema):
    api_version: int
    transaction_id: str
    hotel_id: str
    start_date: date
    end_date: date
    language: str
    customer: Customer
    traveler: GoogleTraveler
    room_rate: GoogleBookingRoomRate
    payment: Optional[GooglePayment] = None
    tracking: Optional[GoogleTracking] = None
    ip_address: Optional[str] = None


class GoogleStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleReservation(BaseSchema):
    locator: Locator
    hotel_locators: List[Locator]
    hotel_id: str
    start_date: date
    end_date: date
    customer: Customer
    traveler: GoogleTraveler
    room_rate: GoogleBookingRoomRate


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleBookingResponse(BaseSchema):
    api_version: int
    transaction_id: str
    status: GoogleStatus
    reservation: GoogleReservation
