import abc
from typing import List, Union

from api.booking.booking_model import HotelBookingRequest, HotelPriceVerificationHolder
from api.common.models import RoomRate
from api.hotel.hotel_model import (
    HotelLocationSearch,
    HotelSpecificSearch,
    CrsHotel,
    HotelDetails,
)


class HotelAdapter(abc.ABC):
    @abc.abstractmethod
    def search_by_location(self, search_request: HotelLocationSearch) -> List[CrsHotel]:
        """Search for a particular location in a remote CRS"""
        pass

    @abc.abstractmethod
    def search_by_id(self, search_request: HotelSpecificSearch) -> CrsHotel:
        """Search for a specific hotel in a remote CRS"""
        pass

    @abc.abstractmethod
    def details(self, *args) -> HotelDetails:
        """Return Hotel Details from a remote CRS"""
        pass

    @abc.abstractmethod
    def booking(self, book_request: HotelBookingRequest):
        """Given a HotelBookingRequest, confirm a reservation in a CRS"""
        pass

    @abc.abstractmethod
    def recheck(self, room_rates: Union[RoomRate, List[RoomRate]]) -> List[RoomRate]:
        """Given a list of RoomRates, recheck prices, and return verified RoomRates"""
        pass
