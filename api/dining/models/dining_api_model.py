import decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from pydantic import Field

from api.common.common_models import SimplenightModel, BusinessLocation


class DiningBase(SimplenightModel):
    date: Optional[str] = None
    time: Optional[str] = None
    covers: Optional[int] = None
    currency: Optional[str] = "USD"


class DiningSearch(DiningBase):
    latitude: Optional[decimal.Decimal] = None
    longitude: Optional[decimal.Decimal] = None


class AdapterDining(SimplenightModel):
    dining_id: str
    name: str
    image: str
    rating: float
    location: BusinessLocation
    phone: str
    openings: Optional[List[str]] = Field(default_factory=list)


class IdSearch(SimplenightModel):
    dining_id: str


class OpeningSearch(DiningBase, IdSearch):
    dining_id: str


class AdapterOpening(SimplenightModel):
    date: date
    times: List[str] = Field(default_factory=list)


class DiningHour(SimplenightModel):
    start: str
    end: str
    day: int


class DiningHours(SimplenightModel):
    __root__: Dict[str, Any]


class DiningDetail(SimplenightModel):
    dining_id: Optional[str]
    name: str
    rating: float
    phone: str
    images: Optional[List[str]] = Field(default_factory=list)
    location: Optional[BusinessLocation]
    is_closed: bool
    display_phone: str
    categories: Optional[List[str]] = Field(default_factory=list)
    hours: List[DiningHours] = Field(default_factory=list)


class DiningUser(SimplenightModel):
    name: str
    image: str


class DiningReview(SimplenightModel):
    rating: float
    text: str
    timestamp: str
    user: DiningUser


class Customer(SimplenightModel):
    first_name: str
    last_name: str
    phone: str
    email: str


class DiningReservationRequest(DiningBase):
    customer: Customer
    user_id: str
    dining_id: str


class DiningReservation(SimplenightModel):
    note: str
    booking_id: str


class AdapterCancelRequest(SimplenightModel):
    booking_id: str
