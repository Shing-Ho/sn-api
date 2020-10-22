import decimal
from datetime import date
from typing import List, Optional

from pydantic import Field

from api.common.models import SimplenightModel
from api.hotel.adapters.hotelbeds.hotelbeds_common_models import (
    HotelBedsAuditDataRS,
    get_language_mapping,
    HotelBedsRateType,
    HotelBedsTaxesRS,
    HotelBedsPromotionsRS,
    HotelBedsCancellationPoliciesRS,
    HotelBedsPaymentType,
)
from api.hotel.models.adapter_models import AdapterLocationSearch


class HotelBedsStayRQ(SimplenightModel):
    checkIn: date = Field(alias="checkIn")
    checkOut: date = Field(alias="checkOut")


class HotelBedsOccupancyRQ(SimplenightModel):
    rooms: int
    adults: int
    children: int


class HotelBedsDestinationRQ(SimplenightModel):
    code: str


class HotelBedsAvailabilityRQ(SimplenightModel):
    stay: HotelBedsStayRQ
    occupancies: List[HotelBedsOccupancyRQ]
    destination: HotelBedsDestinationRQ
    daily_rates: bool = Field(alias="dailyRate", default=False)
    language: str = Field(alias="language", default="ENG")


class HotelBedsRoomRateRS(SimplenightModel):
    rate_key: Optional[str] = Field(alias="rateKey")
    rate_class: str = Field(alias="rateClass")
    rate_type: HotelBedsRateType = Field(alias="rateType")
    net: decimal.Decimal = Field(alias="net", as_string=True)
    allotment: Optional[int] = Field(alias="allotment")
    payment_type: HotelBedsPaymentType = Field(alias="paymentType", by_value=True)
    packaging: bool = Field(alias="packaging")
    rooms: int = Field(alias="rooms")
    adults: int = Field(alias="adults")
    children: int = Field(alias="children")
    taxes: Optional[HotelBedsTaxesRS] = Field(alias="taxes")
    promotions: Optional[List[HotelBedsPromotionsRS]] = Field(alias="promotions", default_factory=list)
    cancellation_policies: Optional[List[HotelBedsCancellationPoliciesRS]] = Field(alias="cancellationPolicies",
                                                                                   default_factory=list)


class HotelBedsRoomRS(SimplenightModel):
    code: str
    name: str
    rates: List[HotelBedsRoomRateRS]


class HotelBedsHotel(SimplenightModel):
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
    rooms: List[HotelBedsRoomRS] = Field(alias="rooms")
    min_rate: Optional[str] = Field(alias="minRate")
    max_rate: Optional[str] = Field(alias="maxRate")
    currency: Optional[str] = Field(alias="currency")


class HotelBedsHotelRS(SimplenightModel):
    checkin: Optional[date] = Field(alias="checkIn")
    checkout: Optional[date] = Field(alias="checkOut")
    total: int = Field(alias="total")
    hotels: Optional[List[HotelBedsHotel]] = Field(default_factory=list)


class HotelBedsError(SimplenightModel):
    code: str
    message: str


class HotelBedsAvailabilityRS(SimplenightModel):
    audit_data: HotelBedsAuditDataRS = Field(alias="auditData")
    results: Optional[HotelBedsHotelRS] = Field(default=None, alias="hotels")
    error: Optional[HotelBedsError] = Field(default=None, alias="error")


class HotelBedsCheckRatesRoom(SimplenightModel):
    rate_key: str = Field(alias="rateKey")


class HotelBedsCheckRatesRQ(SimplenightModel):
    rooms: List[HotelBedsCheckRatesRoom]


class HotelBedsCheckRatesRS(SimplenightModel):
    audit_data: HotelBedsAuditDataRS = Field(alias="auditData")
    hotel: HotelBedsHotel


class HotelBedsSearchBuilder:
    @staticmethod
    def build(request: AdapterLocationSearch) -> HotelBedsAvailabilityRQ:
        stay = HotelBedsStayRQ(checkIn=request.start_date, checkOut=request.end_date)
        destination = HotelBedsDestinationRQ(code=request.location_id)
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
            language=language,
        )

        return request
