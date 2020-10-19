import dataclasses
import decimal
from dataclasses import field
from datetime import date
from enum import Enum
from typing import List, Optional

import marshmallow_dataclass
from marshmallow import EXCLUDE

from api.hotel.adapters.hotelbeds.common_models import (
    HotelBedsAuditDataRS,
    HotelBedsPaymentType,
    HotelBedsTaxesRS,
    HotelBedsPromotionsRS,
    HotelBedsCancellationPoliciesRS,
)
from api.hotel.hotel_api_model import BaseSchema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingLeadTraveler(BaseSchema):
    name: str
    surname: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsPax(BaseSchema):
    roomId: int
    type: str
    name: str
    surname: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingRoom(BaseSchema):
    rateKey: str
    paxes: List[HotelBedsPax]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingRQ(BaseSchema):
    holder: HotelBedsBookingLeadTraveler
    clientReference: str
    rooms: List[HotelBedsBookingRoom]
    remark: Optional[str] = None


class HotelBedsBookingStatus(Enum):
    PRECONFIRMED = "PRECONFIRMED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingModificationPolicy:
    cancellation: bool
    modification: bool


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingRoomRateRS(BaseSchema):
    rate_key: Optional[str] = field(metadata=dict(data_key="rateKey"))
    rate_class: str = field(metadata=dict(data_key="rateClass"))
    net: str = field(metadata=dict(data_key="net"))
    payment_type: HotelBedsPaymentType = field(metadata=dict(data_key="paymentType", by_value=True))
    packaging: bool = field(metadata=dict(data_key="packaging"))
    rooms: int = field(metadata=dict(data_key="rooms"))
    adults: int = field(metadata=dict(data_key="adults"))
    children: int = field(metadata=dict(data_key="children"))
    taxes: Optional[HotelBedsTaxesRS] = field(metadata=dict(data_key="taxes"))
    promotions: Optional[List[HotelBedsPromotionsRS]] = field(
        metadata=dict(data_key="promotions"), default_factory=list
    )
    cancellation_policies: Optional[List[HotelBedsCancellationPoliciesRS]] = field(
        metadata=dict(data_key="cancellationPolicies"), default_factory=list
    )


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingRoomRS(BaseSchema):
    code: str
    name: str
    rates: List[HotelBedsBookingRoomRateRS]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingHotel(BaseSchema):
    code: int = field(metadata=dict(data_key="code"))
    name: str = field(metadata=dict(data_key="name"))
    category_code: str = field(metadata=dict(data_key="categoryCode"))
    category_name: str = field(metadata=dict(data_key="categoryName"))
    destination_code: str = field(metadata=dict(data_key="destinationCode"))
    destination_name: str = field(metadata=dict(data_key="destinationName"))
    zone_code: int = field(metadata=dict(data_key="zoneCode"))
    zone_name: str = field(metadata=dict(data_key="zoneName"))
    latitude: str = field(metadata=dict(data_key="latitude"))
    longitude: str = field(metadata=dict(data_key="longitude"))
    rooms: List[HotelBedsBookingRoomRS] = field(metadata=dict(data_key="rooms"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingDetailRS:
    class Meta:
        unknown = EXCLUDE

    reference: str
    client_reference: str = field(metadata=dict(data_key="clientReference"))
    creation_date: date = field(metadata=dict(data_key="creationDate"))
    status: HotelBedsBookingStatus
    modification_policies: HotelBedsBookingModificationPolicy = field(metadata=dict(data_key="modificationPolicies"))
    hotel: HotelBedsBookingHotel
    pending_amount: decimal.Decimal = field(metadata=dict(data_key="pendingAmount", as_string=True))
    total_net: decimal.Decimal = field(metadata=dict(data_key="totalNet", as_string=True))
    holder: HotelBedsBookingLeadTraveler
    remark: Optional[str]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsBookingRS(BaseSchema):
    audit_data: HotelBedsAuditDataRS = field(metadata=dict(data_key="auditData"))
    booking: HotelBedsBookingDetailRS
