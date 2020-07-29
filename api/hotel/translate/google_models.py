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

from api.booking.booking_model import Customer, PaymentMethod, CardType
from api.common.models import BaseSchema, Address, Money, RemoveNone
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
class BaseGoogleRoomRate(BaseSchema):
    code: str
    room_type_code: str
    rate_plan_code: str
    maximum_allowed_occupancy: RoomCapacity
    total_price_at_booking: Optional[Money]
    total_price_at_checkout: Optional[Money]


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


class GoogleSubmitErrorType(Enum):
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    API_VERSION_UNSUPPORTED = "API_VERSION_UNSUPPORTED"
    CHECKIN_TOO_CLOSE = "CHECKIN_TOO_CLOSE"
    CUSTOMER_NAME_INVALID = "CUSTOMER_NAME_INVALID"
    DATE_SELECTION_INVALID = "DATE_SELECTION_INVALID"
    DUPLICATE_BOOKING = "DUPLICATE_BOOKING"
    HOTEL_NOT_FOUND = "HOTEL_NOT_FOUND"
    NETWORK_ERROR = "NETWORK_ERROR"
    PAYMENT_BILLING_ADDRESS_INVALID = "PAYMENT_BILLING_ADDRESS_INVALID"
    PAYMENT_CARD_CARDHOLDER_NAME_INVALID = "PAYMENT_CARD_CARDHOLDER_NAME_INVALID"
    PAYMENT_CARD_CVC_INVALID = "PAYMENT_CARD_CVC_INVALID"
    PAYMENT_CARD_EXPIRATION_INVALID = "PAYMENT_CARD_EXPIRATION_INVALID"
    PAYMENT_CARD_NUMBER_INVALID = "PAYMENT_CARD_NUMBER_INVALID"
    PAYMENT_CARD_TYPE_NOT_SUPPORTED = "PAYMENT_CARD_TYPE_NOT_SUPPORTED"
    PAYMENT_DECLINED = "PAYMENT_DECLINED"
    PAYMENT_INVALID = "PAYMENT_INVALID"
    PAYMENT_INSUFFICIENT = "PAYMENT_INSUFFICIENT"
    PAYMENT_PROCESSOR_ERROR = "PAYMENT_PROCESSOR_ERROR"
    PAYMENT_TYPE_NOT_ACCEPTED = "PAYMENT_TYPE_NOT_ACCEPTED"
    RATE_PLAN_UNAVAILABLE = "RATE_PLAN_UNAVAILABLE"
    RECOVERABLE_ERROR = "RECOVERABLE_ERROR"
    REQUEST_DATA_INVALID = "REQUEST_DATA_INVALID"
    REQUEST_INCOMPLETE = "REQUEST_INCOMPLETE"
    REQUEST_NOT_PARSABLE = "REQUEST_NOT_PARSABLE"
    ROOM_RATE_MISMATCH = "ROOM_RATE_MISMATCH"
    ROOM_RATE_PRICE_MISMATCH = "ROOM_RATE_PRICE_MISMATCH"
    ROOM_RATE_UNAVAILABLE = "ROOM_RATE_UNAVAILABLE"
    ROOM_TYPE_UNAVAILABLE = "ROOM_TYPE_UNAVAILABLE"
    TRAVELER_NAME_INVALID = "TRAVELER_NAME_INVALID"
    SUPPLIER_ERROR = "SUPPLIER_ERROR"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class GoogleSubmitError:
    type: GoogleSubmitErrorType
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
