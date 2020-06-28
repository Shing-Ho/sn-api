import dataclasses
from dataclasses import field
from datetime import date, datetime
from enum import Enum
from typing import ClassVar, Type, List, Optional

import marshmallow_dataclass
from marshmallow import Schema

from api.hotel.hotels import HotelLocationSearch, BaseSchema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsStay(BaseSchema):
    checkin: date = field(metadata=dict(data_key="checkIn"))
    checkout: date = field(metadata=dict(data_key="checkOut"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsOccupancy(BaseSchema):
    rooms: int
    adults: int
    children: int


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsDestination(BaseSchema):
    code: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsAvailabilityRQ(BaseSchema):
    stay: HotelBedsStay
    occupancies: List[HotelBedsOccupancy]
    destination: HotelBedsDestination

    Schema: ClassVar[Type[Schema]] = Schema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsAuditData(BaseSchema):
    timestamp: datetime
    environment: str
    release: str
    process_time: str = field(metadata=dict(data_key="processTime"))
    request_host: str = field(metadata=dict(data_key="requestHost"))
    server_id: str = field(metadata=dict(data_key="serverId"))


class HotelBedsRateType(Enum):
    BOOKABLE = "BOOKABLE"
    RECHECK = "RECHECK"


class HotelBedsPaymentType(Enum):
    AT_HOTEL = "AT_HOTEL"
    AT_WEB = "AT_WEB"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsCancellationPolicies(BaseSchema):
    deadline: datetime = field(metadata=dict(data_key="from"))
    amount: str = field(metadata=dict(data_key="amount"))


class HotelBedsTaxType(Enum):
    TAX = "TAX"
    FEE = "FEE"
    TAXESANDFEE = "TAXESANDFEE"


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsTax(BaseSchema):
    included: bool
    amount: str
    currency: str
    type: Optional[HotelBedsTaxType]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsTaxes(BaseSchema):
    taxes: List[HotelBedsTax] = field(metadata=dict(data_key="taxes"))
    all_included: bool = field(metadata=dict(data_key="allIncluded"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsPromotions(BaseSchema):
    code: str
    name: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsRoomRate(BaseSchema):
    rate_key: str = field(metadata=dict(data_key="rateKey"))
    rate_class: str = field(metadata=dict(data_key="rateClass"))
    rate_type: HotelBedsRateType = field(metadata=dict(data_key="rateType"))
    net: str = field(metadata=dict(data_key="net"))
    allotment: int = field(metadata=dict(data_key="allotment"))
    payment_type: HotelBedsPaymentType = field(metadata=dict(data_key="paymentType", by_value=True))
    packaging: bool = field(metadata=dict(data_key="packaging"))
    rooms: int = field(metadata=dict(data_key="rooms"))
    adults: int = field(metadata=dict(data_key="adults"))
    children: int = field(metadata=dict(data_key="children"))
    taxes: Optional[HotelBedsTaxes] = field(metadata=dict(data_key="taxes"))
    promotions: Optional[List[HotelBedsPromotions]] = field(metadata=dict(data_key="promotions"), default_factory=list)
    cancellation_policies: Optional[List[HotelBedsCancellationPolicies]] = field(
        metadata=dict(data_key="cancellationPolicies"), default_factory=list
    )


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsRoom(BaseSchema):
    code: str
    name: str
    rates: List[HotelBedsRoomRate]


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsHotel(BaseSchema):
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
    rooms: List[HotelBedsRoom] = field(metadata=dict(data_key="rooms"))
    min_rate: str = field(metadata=dict(data_key="minRate"))
    max_rate: str = field(metadata=dict(data_key="maxRate"))
    currency: Optional[str] = field(metadata=dict(data_key="currency"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsHotelRS(BaseSchema):
    checkin: date = field(metadata=dict(data_key="checkIn"))
    checkout: date = field(metadata=dict(data_key="checkOut"))
    total: int = field(metadata=dict(data_key="total"))
    hotels: List[HotelBedsHotel] = field(default_factory=list)


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsAvailabilityRS(BaseSchema):
    audit_data: HotelBedsAuditData = field(metadata=dict(data_key="auditData"))
    results: HotelBedsHotelRS = field(metadata=dict(data_key="hotels"))


class HotelBedsSearchBuilder:
    @staticmethod
    def build(request: HotelLocationSearch) -> HotelBedsAvailabilityRQ:
        stay = HotelBedsStay(request.checkin_date, request.checkout_date)
        destination = HotelBedsDestination(request.location_name)
        occupancy = [HotelBedsOccupancy(request.num_rooms, request.num_adults, request.num_children)]

        request = HotelBedsAvailabilityRQ(stay, occupancy, destination)

        return request
