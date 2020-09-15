from api.booking.booking_model import HotelBookingRequest
from api.hotel.adapters.tripservices.transport import TripServicesTransport
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import (
    HotelDetails,
    HotelLocationSearch,
    HotelSpecificSearch,
    AdapterHotel,
    BaseHotelSearch,
)
from typing import List


class TripservicesAdapter(HotelAdapter):
    def __init__(self, transport=None):
        self.transport = transport
        if self.transport is None:
            self.transport = TripServicesTransport()

    def search_by_location(self, search_request: HotelLocationSearch) -> List[AdapterHotel]:
        # request = self._create_city_search(search_request)
        pass

    def search_by_id(self, search: HotelSpecificSearch) -> AdapterHotel:
        pass

    def details(self, *args) -> HotelDetails:
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass

    def _create_city_search(self, search: HotelLocationSearch):
        return {
            **self._create_base_search(search),
            "city": search.location_name,
        }

    @staticmethod
    def _create_base_search(search: BaseHotelSearch):
        params = {
            "check_in": search.start_date,
            "check_out": search.end_date,
            "adults": search.occupancy.adults,
            "children": search.occupancy.children,
            "limit": 2,
        }

        if search.currency:
            params["currency"] = search.currency

        return params
