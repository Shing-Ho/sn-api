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
class HotelAdapterHotel:
    name: str
    chain_code: str
    address: HotelAddress
    rate: HotelRate
    star_rating: Optional[int] = None


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search(self, search_request: HotelSearchRequest) -> List[HotelAdapterHotel]:
        pass
