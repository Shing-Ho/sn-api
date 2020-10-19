import decimal
from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import Field

from api.common.models import SimplenightModel
from api.hotel.adapters.hotelbeds.common_models import (
    HotelBedsAuditDataRS,
    HotelBedsPaymentType,
    HotelBedsTaxesRS,
    HotelBedsPromotionsRS,
    HotelBedsCancellationPoliciesRS,
)


class HotelBedsBookingLeadTraveler(SimplenightModel):
    name: str
    surname: str


class HotelBedsPax(SimplenightModel):
    roomId: int
    type: str
    name: str
    surname: str


class HotelBedsBookingRoom(SimplenightModel):
    rateKey: str
    paxes: List[HotelBedsPax]


class HotelBedsBookingRQ(SimplenightModel):
    holder: HotelBedsBookingLeadTraveler
    clientReference: str
    rooms: List[HotelBedsBookingRoom]
    remark: Optional[str] = None


class HotelBedsBookingStatus(Enum):
    PRECONFIRMED = "PRECONFIRMED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class HotelBedsBookingModificationPolicy(SimplenightModel):
    cancellation: bool
    modification: bool


class HotelBedsBookingRoomRateRS(SimplenightModel):
    rate_key: Optional[str] = Field(alias="rateKey")
    rate_class: str = Field(alias="rateClass")
    net: str = Field(alias="net")
    payment_type: HotelBedsPaymentType = Field(alias="paymentType", by_value=True)
    packaging: bool = Field(alias="packaging")
    rooms: int = Field(alias="rooms")
    adults: int = Field(alias="adults")
    children: int = Field(alias="children")
    taxes: Optional[HotelBedsTaxesRS] = Field(alias="taxes")
    promotions: Optional[List[HotelBedsPromotionsRS]] = Field(alias="promotions", default_factory=list)
    cancellation_policies: Optional[List[HotelBedsCancellationPoliciesRS]] = Field(
        alias="cancellationPolicies", default_factory=list
    )


class HotelBedsBookingRoomRS(SimplenightModel):
    code: str
    name: str
    rates: List[HotelBedsBookingRoomRateRS]


class HotelBedsBookingHotel(SimplenightModel):
    code: int = Field(alias="code")
    name: str = Field(alias="name")
    category_code: str = Field(alias="categoryCode")
    category_name: str = Field(alias="categoryName")
    destination_code: str = Field(alias="destinationCode")
    destination_name: str = Field(alias="destinationName")
    zone_code: int = Field(alias="zoneCode")
    zone_name: str = Field(alias="zoneName")
    latitude: str = Field(alias="latitude")
    longitude: str = Field(alias="longitude")
    rooms: List[HotelBedsBookingRoomRS] = Field(alias="rooms")


class HotelBedsBookingDetailRS(SimplenightModel):
    reference: str
    client_reference: str = Field(alias="clientReference")
    creation_date: date = Field(alias="creationDate")
    status: HotelBedsBookingStatus
    modification_policies: HotelBedsBookingModificationPolicy = Field(alias="modificationPolicies")
    hotel: HotelBedsBookingHotel
    pending_amount: decimal.Decimal = Field(alias="pendingAmount")
    total_net: decimal.Decimal = Field(alias="totalNet")
    holder: HotelBedsBookingLeadTraveler
    remark: Optional[str]


class HotelBedsBookingRS(SimplenightModel):
    audit_data: HotelBedsAuditDataRS = Field(alias="auditData")
    booking: HotelBedsBookingDetailRS
