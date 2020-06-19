import abc
from typing import List
from api.hotel.hotels import (
    HotelLocationSearch,
    HotelAdapterHotel,
    HotelSpecificSearch,
    HotelSearchResponse,
    HotelDetails
)


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelAdapterHotel]:
        pass

    @abc.abstractmethod
    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponse:
        pass

    @abc.abstractmethod
    def details(self, *args) -> HotelDetails:
        pass