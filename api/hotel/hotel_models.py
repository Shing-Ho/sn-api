from datetime import date
from typing import Optional

from pydantic.main import BaseModel


class AdapterModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class AdapterOccupancy(AdapterModel):
    adults: Optional[int] = 1
    children: Optional[int] = 0
    num_rooms: Optional[int] = 1


class AdapterBaseSearch(AdapterModel):
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
