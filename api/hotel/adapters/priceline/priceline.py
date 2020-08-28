from typing import Union, List

from api.booking.booking_model import HotelBookingRequest
from api.common.models import RoomRate
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import HotelDetails, HotelSpecificSearch, CrsHotel, HotelLocationSearch


class PricelineAdapter(HotelAdapter):
    def search_by_location(self, search_request: HotelLocationSearch) -> List[CrsHotel]:
        pass

    def search_by_id(self, search_request: HotelSpecificSearch) -> CrsHotel:
        pass

    def details(self, *args) -> HotelDetails:
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass

    def recheck(self, room_rates: Union[RoomRate, List[RoomRate]]) -> List[RoomRate]:
        pass