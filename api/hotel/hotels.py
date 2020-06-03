import abc
from dataclasses import dataclass, field
from typing import List


@dataclass
class HotelSearchRequest:
    location_name: str
    num_rooms: int


@dataclass
class HotelAddress:
    city: str
    region: str
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


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search(self, search_request: HotelSearchRequest) -> List[HotelAdapterHotel]:
        pass
