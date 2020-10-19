import dataclasses
from datetime import date
from enum import Enum
from typing import Optional, List, Union

import marshmallow_dataclass
from marshmallow import validates_schema

from api.common.models import BaseSchema, RoomOccupancy, Address, RoomRate, RemoveNone
from api.hotel.hotel_api_model import CancellationDetails


class SubmitErrorType(Enum):
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


class PaymentMethod(Enum):
    PAYMENT_TOKEN = "PAYMENT_TOKEN"
    CREDIT_CARD = "CREDIT_CARD"
    PAYMENT_CARD = "PAYMENT_CARD"


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
    billing_address: Address
    payment_card_parameters: Optional[PaymentCardParameters] = None
    payment_token: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None

    # noinspection PyUnusedLocal
    @validates_schema
    def validate(self, data, *args, **kwargs):
        if data["payment_method"] == PaymentMethod.PAYMENT_TOKEN and not data["payment_token"]:
            raise ValueError(f"Must set payment_token when payment_method is {PaymentMethod.PAYMENT_TOKEN.value}")

        if data["payment_method"] == PaymentMethod.CREDIT_CARD and not data["payment_card_parameters"]:
            raise ValueError(
                f"Must set payment_card_parameters when payment_method is {PaymentMethod.CREDIT_CARD.value}"
            )


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBookingRequest(BaseSchema):
    api_version: int
    transaction_id: str
    hotel_id: str
    room_code: str
    language: str
    customer: Customer
    traveler: Traveler
    payment: Optional[Payment] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Status(BaseSchema):
    success: bool
    message: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Locator(BaseSchema, RemoveNone):
    id: str
    pin: Optional[str] = None


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class Reservation(BaseSchema):
    locator: Locator
    hotel_locator: Optional[Union[List[Locator], Locator]]
    hotel_id: str
    checkin: date
    checkout: date
    customer: Customer
    traveler: Traveler
    room_rate: RoomRate
    cancellation_details: List[CancellationDetails] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBookingResponse(BaseSchema):
    api_version: int
    transaction_id: str
    booking_id: str
    status: Status
    reservation: Reservation


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelPriceVerificationHolder:
    original_room_rates: List[RoomRate]
    verified_room_rates: List[RoomRate]
