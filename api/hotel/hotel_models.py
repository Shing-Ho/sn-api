from datetime import date
from typing import Optional, List

from api.common.models import SimplenightModel, RoomOccupancy, RoomRate
from api.hotel.hotel_api_model import RoomType, RatePlan, HotelDetails, ErrorResponse


class AdapterOccupancy(SimplenightModel):
    adults: Optional[int] = 1
    children: Optional[int] = 0
    num_rooms: Optional[int] = 1


class AdapterBaseSearch(SimplenightModel):
    start_date: date
    end_date: date
    occupancy: AdapterOccupancy
    language: str = "en"
    currency: str = "USD"


class AdapterHotelSearch(AdapterBaseSearch):
    provider_hotel_id: str
    simplenight_hotel_id: str


class AdapterLocationSearch(AdapterBaseSearch):
    location_id: str


class AdapterHotel(SimplenightModel):
    provider: str
    hotel_id: str
    start_date: date
    end_date: date
    occupancy: RoomOccupancy
    room_types: List[RoomType]
    rate_plans: Optional[List[RatePlan]] = None
    room_rates: Optional[List[RoomRate]] = None
    hotel_details: Optional[HotelDetails] = None
    error: Optional[ErrorResponse] = None


class AdapterHotelList(SimplenightModel):
    __root__: List[AdapterHotel]
