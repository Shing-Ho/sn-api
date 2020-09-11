import abc
from typing import List

from api.booking.booking_model import HotelBookingRequest, HotelBookingResponse
from api.common.models import RoomRate
from api.hotel.hotel_model import (
    HotelLocationSearch,
    HotelSpecificSearch,
    AdapterHotel,
    HotelDetails,
)


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search_by_location(self, search_request: HotelLocationSearch) -> List[AdapterHotel]:
        """Search a provider for a particular location"""
        pass

    @abc.abstractmethod
    def search_by_id(self, search_request: HotelSpecificSearch) -> AdapterHotel:
        """Search a hotel provider for a specific hotel"""
        pass

    @abc.abstractmethod
    def details(self, *args) -> HotelDetails:
        """Return Hotel Details using a hotel provider"""
        pass

    @abc.abstractmethod
    def booking(self, book_request: HotelBookingRequest) -> HotelBookingResponse:
        """Given a HotelBookingRequest, confirm a reservation with a hotel provider"""
        pass

    @abc.abstractmethod
    def recheck(self, room_rate: RoomRate) -> RoomRate:
        """Given a list of RoomRates, recheck prices, and return verified RoomRates"""
        pass
