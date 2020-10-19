from typing import List, Optional

from pydantic import Field

from api.common.models import SimplenightModel
from api.hotel.adapters.hotelbeds.common_models import HotelBedsAuditDataRS, HotelBedsCoordinates


class HotelBedsContent(SimplenightModel):
    content: str
    street: Optional[str]
    number: Optional[str]


class HotelBedsPhone(SimplenightModel):
    phone_number: str = Field(alias="phoneNumber")
    phone_type: str = Field(alias="phoneType")


class HotelBedsImage(SimplenightModel):
    image_type: str = Field(alias="imageTypeCode")
    path: str = Field(alias="path")
    order: int = Field(alias="order")


class HotelBedsAmenity(SimplenightModel):
    facility_code: int = Field(alias="facilityCode")
    facility_group_code: int = Field(alias="facilityGroupCode")


class HotelBedsHotelDetail(SimplenightModel):
    code: int = Field(alias="code")
    name: HotelBedsContent = Field(alias="name")
    description: Optional[HotelBedsContent] = Field(alias="description")
    category_code: str = Field(alias="categoryCode")
    country_code: str = Field(alias="countryCode")
    state_code: str = Field(alias="stateCode")
    coordinates: HotelBedsCoordinates = Field(alias="coordinates")
    chain_code: Optional[str] = Field(alias="chainCode")
    amenities: Optional[List[HotelBedsAmenity]] = Field(alias="facilities")
    accommodation_type: str = Field(alias="accommodationTypeCode")
    address: HotelBedsContent = Field(alias="address")
    postal_code: Optional[str] = Field(alias="postalCode")
    city: HotelBedsContent = Field(alias="city")
    email: Optional[str] = Field(alias="email")
    phones: List[HotelBedsPhone] = Field(alias="phones", default_factory=list)
    images: List[HotelBedsImage] = Field(alias="images", default_factory=list)


class HotelBedsHotelDetailsRS(SimplenightModel):
    start: int = Field(alias="from")
    end: int = Field(alias="to")
    total: int = Field(alias="total")
    audit_data: HotelBedsAuditDataRS = Field(alias="auditData")
    hotels: List[HotelBedsHotelDetail]
