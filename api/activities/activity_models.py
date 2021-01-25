from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union

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
    activity_dates: List[Union[datetime, date, str]]
    activity_times: List[str]
    capacity: int
    uuid: str


class ActivityCancellation(SimplenightModel):
    type: str
    label: str


class ActivityItem(SimplenightModel):
    category: Optional[Union[str, List[str]]] = Field(default_factory=list)
    code: str
    status: str
    price: Decimal
    price_type: str


class ActivityVariants(SimplenightModel):
    code: str
    name: str
    description: str
    capacity: int
    status: str
    price: Decimal
    currency: str


class SimplenightActivityVariantRequest(SimplenightModel):
    code: str
    activity_date: date


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
