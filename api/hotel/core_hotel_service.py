import abc
from typing import List

from api.booking.booking_model import HotelBookingRequest
from api.common.models import RoomRate
from api.hotel.hotel_model import (
    HotelSpecificSearch,
    HotelLocationSearch,
    Hotel,
    HotelDetailsSearchRequest,
    HotelDetails
)


class HotelService(abc.ABC):
    def search_by_location(self, search_request: HotelLocationSearch) -> List[Hotel]:
        pass

    def search_by_id(self, search_request: HotelSpecificSearch) -> Hotel:
        pass

    def details(self, hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
        pass

    def recheck(self, provider: str, room_rate: List[RoomRate]) -> List[RoomRate]:
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass
