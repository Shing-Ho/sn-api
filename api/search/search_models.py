from datetime import date
from enum import Enum
from typing import List, Optional

from api.common.common_models import SimplenightModel
from api.hotel.models.hotel_api_model import HotelSearch


class Products(Enum):
    HOTELS = "hotels"
    ACTIVITIES = "activities"
    DINING = "dining"
    EVENTS = "events"


class ActivitySearch(SimplenightModel):
    activity_date: date
    adults: int
    children: int
    provider: Optional[str] = None


class ActivityLocationSearch(ActivitySearch):
    location_id: str


class ActivitySpecificSearch(ActivitySearch):
    activity_id: str


class SearchRequest(SimplenightModel):
    product_types: List[Products]
    hotel_search: Optional[HotelSearch]
    activity_search: Optional[ActivitySearch]
