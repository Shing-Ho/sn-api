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
    adults: int
    children: int


class SearchRequest(SimplenightModel):
    begin_date: date
    end_date: Optional[date]
    location_id: str
    product_types: List[Products]
    hotel_search: Optional[HotelSearch]
    activity_search: Optional[ActivitySearch]
