import abc
from typing import List, Union

from api.booking.booking_model import HotelBookingRequest
from api.common.models import RoomRate
from api.hotel.hotel_model import (
    HotelLocationSearch,
    HotelSpecificSearch,
    HotelSearchResponseHotel,
    HotelDetails,
    HotelPriceChange,
)


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelSearchResponseHotel]:
        pass

    @abc.abstractmethod
    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponseHotel:
        pass

    @abc.abstractmethod
    def details(self, *args) -> HotelDetails:
        pass

    @abc.abstractmethod
    def booking(self, book_request: HotelBookingRequest):
        pass

    @abc.abstractmethod
    def recheck(self, room_rates: Union[RoomRate, List[RoomRate]]) -> HotelPriceChange:
        pass
