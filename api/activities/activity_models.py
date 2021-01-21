from datetime import date
from decimal import Decimal
from typing import List

from pydantic import Field

from api.common.common_models import SimplenightModel, BusinessContact, BusinessLocation
from api.hotel.models.hotel_api_model import Image
from api.hotel.models.hotel_common_models import Money


class SimplenightActivity(SimplenightModel):
    name: str
    code: str
    description: str
    activity_date: date
    total_price: Money
    total_base: Money
    total_taxes: Money
    images: List[Image]


class ActivityAvailabilityTime(SimplenightModel):
    type: str
    label: str
    days: List[str]
    times: List[str]
    capacity: int
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")
    uuid: str


class ActivityCancellation(SimplenightModel):
    type: str
    label: str


class ActivityItem(SimplenightModel):
    category: List[str]
    code: str
    status: str
    price: Decimal
    price_type: str


class SimplenightActivityDetailRequest(SimplenightModel):
    code: str
    date_from: date
    date_to: date


class SimplenightActivityDetailResponse(SimplenightModel):
    code: str
    type: str
    categories: List[str]
    timezone: str
    images: List[Image]
    contact: BusinessContact
    locations: List[BusinessLocation]
    availabilities: List[ActivityAvailabilityTime]
    policies: List[str]
    cancellations: List[ActivityCancellation]
    items: List[ActivityItem]
