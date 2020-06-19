import abc
from dataclasses import dataclass, field
from datetime import date
from typing import List, Union, Optional


@dataclass
class HotelSearchRequest:
    location_name: str
    checkin_date: Union[date, str]
    checkout_date: Union[date, str]
    num_rooms: int = 1
    num_adults: int = 1
    num_children: int = 0
    checkin_time: str = None
    checkout_time: str = None


@dataclass
class HotelDetailsSearchRequest:
    chain_code: str
    hotel_code: str
    checkin_date: date
    checkout_date: date
    num_rooms: int = 1
    currency: str = "USD"


@dataclass
class HotelAddress:
    city: str
    region: str
    postal_code: str
    country: str
    address_lines: List[str] = field(default_factory=list)


@dataclass
class HotelRate:
    total_price: float
    taxes: float


@dataclass
class Phone:
    type: str
    number: str
    extension: str


@dataclass
class HotelAdapterHotel:
    name: str
    chain_code: str
    address: HotelAddress
    rate: HotelRate
    star_rating: Optional[int] = None


@dataclass
class HotelCommission:
    has_commission: bool
    percent: int
    amount: int = 0


@dataclass
class RateCancelInfo:
    refundable: bool


@dataclass
class Money:
    amount: float
    currency: str


@dataclass
class DailyRate:
    rate_date: date
    base_rate: Money
    tax: Money
    total: Money


@dataclass
class RoomRate:
    description: str
    additional_detail: List[str]
    rate_plan_type: str
    total_base_rate: Money
    total_tax_rate: Money
    total: Money
    daily_rates: List[DailyRate] = field(default_factory=list)


@dataclass
class HotelDetails:
    name: str
    chain_code: str
    hotel_code: str
    checkin_time: str
    checkout_time: str
    hotel_rates: List[RoomRate]


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search(self, search_request: HotelSearchRequest) -> List[HotelAdapterHotel]:
        pass

    @abc.abstractmethod
    def details(self, *args):
        pass
