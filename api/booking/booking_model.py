import dataclasses
from datetime import date
from enum import Enum
from typing import Optional, List

import marshmallow_dataclass
from marshmallow import validates_schema

from api.common.models import BaseSchema, RoomOccupancy, Address, RoomRate


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
    checkin: date
    checkout: date
    language: str
    customer: Customer
    traveler: Traveler
    room_rates: List[RoomRate] = dataclasses.field(default_factory=list)
    payment: Optional[Payment] = None
    tracking: Optional[str] = None
    ip_address: Optional[str] = None
    crs: str = "stub"


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
