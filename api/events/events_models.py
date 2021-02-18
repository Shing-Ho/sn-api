from datetime import date
from decimal import Decimal
from typing import List, Optional

from api.common.common_models import SimplenightModel
from api.hotel.models.hotel_api_model import Image
from api.hotel.models.hotel_common_models import Money
from api.locations.models import Location


class EventAdapterLocationSearch(SimplenightModel):
    begin_date: date
    end_date: date
    location: Location


class EventLocation(SimplenightModel):
    name: str
    address: str
    latitude: Decimal
    longitude: Decimal


class EventItem(SimplenightModel):
    code: str
    price: Money
    name: str


class SimplenightEvent(SimplenightModel):
    name: str
    code: str
    description: str
    seating_chart: str
    items: List[EventItem]
    location: Optional[EventLocation]
    categories: Optional[List[str]]
    images: List[Image]


class AdapterEvent(SimplenightModel):
    provider: str
    name: str
    code: str
    description: str
    seating_chart: str
    items: List[EventItem]
    location: Optional[EventLocation]
    categories: Optional[List[str]]
    images: List[Image]


class EventDataCachePayload(SimplenightModel):
    code: str
    provider: str
    adapter_activity: AdapterEvent
    simplenight_activity: SimplenightEvent
