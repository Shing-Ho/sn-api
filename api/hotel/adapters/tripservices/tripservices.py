from typing import List

from api.hotel.models.booking_model import HotelBookingRequest
from api.hotel.models.hotel_common_models import RoomRate
from api.hotel.adapters.tripservices.transport import TripServicesTransport
from api.hotel.adapters.tripservices.tripservices_info import TripservicesInfo
from api.hotel.adapters.hotel_adapter import HotelAdapter
from api.hotel.models.hotel_api_model import (
    HotelDetails,
    AdapterHotel,
)
from api.hotel.models.adapter_models import AdapterHotelSearch, AdapterLocationSearch, AdapterBaseSearch, \
    AdapterCancelRequest, AdapterCancelResponse


class TripservicesAdapter(HotelAdapter):
    def __init__(self, transport=None):
        self.transport = transport
        if self.transport is None:
            self.transport = TripServicesTransport()

    def search_by_location(self, search: AdapterLocationSearch) -> List[AdapterHotel]:
        # request = self._create_city_search(search_request)
        pass

    def search_by_id(self, search: AdapterHotelSearch) -> AdapterHotel:
        pass

    def details(self, *args) -> HotelDetails:
        pass

    def cancel(self, cancel_request: AdapterCancelRequest) -> AdapterCancelResponse:
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass

    def _create_city_search(self, search: AdapterLocationSearch):
        return {
            **self._create_base_search(search),
            "city": search.location_id,
        }

    @staticmethod
    def _create_base_search(search: AdapterBaseSearch):
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

    def recheck(self, room_rate: RoomRate) -> RoomRate:
        pass

    @classmethod
    def factory(cls, test_mode=True):
        return TripservicesAdapter(TripservicesAdapter())

    def get_provider_name(self):
        TripservicesInfo.get_name()
