import dataclasses
from dataclasses import field
from datetime import date
from typing import ClassVar, Type, List, Optional

import marshmallow_dataclass
from marshmallow import Schema

from api.hotel.adapters.hotelbeds.common import (
    HotelBedsAuditDataRS,
    get_language_mapping,
    HotelBedsRateType,
    HotelBedsTaxesRS,
    HotelBedsPromotionsRS,
    HotelBedsCancellationPoliciesRS,
    HotelBedsPaymentType,
)
from api.hotel.hotels import HotelLocationSearch, BaseSchema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsStayRQ(BaseSchema):
    checkin: date = field(metadata=dict(data_key="checkIn"))
    checkout: date = field(metadata=dict(data_key="checkOut"))


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsOccupancyRQ(BaseSchema):
    rooms: int
    adults: int
    children: int


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsDestinationRQ(BaseSchema):
    code: str


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsAvailabilityRQ(BaseSchema):
    stay: HotelBedsStayRQ
    occupancies: List[HotelBedsOccupancyRQ]
    destination: HotelBedsDestinationRQ
    daily_rates: bool = field(metadata=dict(data_key="dailyRate"), default=False)
    language: str = field(metadata=dict(data_key="language"), default="ENG")

    Schema: ClassVar[Type[Schema]] = Schema


@dataclasses.dataclass
@marshmallow_dataclass.dataclass
class HotelBedsRoomRateRS(BaseSchema):
    rate_key: Optional[str] = field(metadata=dict(data_key="rateKey"))
    rate_class: str = field(metadata=dict(data_key="rateClass"))
    rate_type: HotelBedsRateType = field(metadata=dict(data_key="rateType"))
    net: str = field(metadata=dict(data_key="net"))
    allotment: int = field(metadata=dict(data_key="allotment"))
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
class HotelBedsRoomRS(BaseSchema):
    code: str
    name: str
    rates: List[HotelBedsRoomRateRS]


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
    rooms: List[HotelBedsRoomRS] = field(metadata=dict(data_key="rooms"))
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
    audit_data: HotelBedsAuditDataRS = field(metadata=dict(data_key="auditData"))
    results: HotelBedsHotelRS = field(metadata=dict(data_key="hotels"))


class HotelBedsSearchBuilder:
    @staticmethod
    def build(request: HotelLocationSearch) -> HotelBedsAvailabilityRQ:
        stay = HotelBedsStayRQ(request.checkin_date, request.checkout_date)
        destination = HotelBedsDestinationRQ(request.location_name)
        language = get_language_mapping(request.language)
        occupancy = [
            HotelBedsOccupancyRQ(
                rooms=request.occupancy.num_rooms, adults=request.occupancy.adults, children=request.occupancy.children,
            )
        ]

        request = HotelBedsAvailabilityRQ(
            stay=stay,
            occupancies=occupancy,
            destination=destination,
            daily_rates=request.daily_rates,
            language=language,
        )

        return request
