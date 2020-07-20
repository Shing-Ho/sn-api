from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from api.booking.booking_model import HotelBookingRequest
from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.adapters.travelport.transport import TravelportTransport
from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.hotel.hotel_model import (
    HotelDetails,
    HotelSpecificSearch,
    HotelSearchResponseHotel,
    HotelLocationSearch,
    HotelDetailsSearchRequest,
    BaseHotelSearch,
)

HOTEL_ADAPTERS = {
    "stub": StubHotelAdapter(),
    "travelport": TravelportHotelAdapter(TravelportTransport()),
    "hotelbeds": HotelBeds(HotelBedsTransport()),
}


class HotelService:
    MAX_WORKERS = 5

    def __init__(self, adapters):
        self.adapters = adapters

    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelSearchResponseHotel]:
        futures = []
        all_hotels = []

        adapters = self._get_adapters(search_request.crs)
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            for adapter in adapters:
                futures.append(executor.submit(adapter.search_by_location, search_request))

            for future in futures:
                all_hotels.extend(future.result())

        return all_hotels

    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponseHotel:
        adapter = self._get_adapters(search_request.crs)[0]
        return adapter.search_by_id(search_request)

    def details(self, hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
        adapter = self._get_adapters(hotel_details_req.crs)[0]
        return adapter.details(hotel_details_req)

    def recheck(self, crs: str, search: BaseHotelSearch, rate_key: str) -> HotelSearchResponseHotel:
        adapter = self._get_adapters(crs)[0]
        return adapter.recheck(search, rate_key)

    def booking_availability(self, search_request: HotelSpecificSearch):
        adapter = self._get_adapters(search_request.crs)[0]
        return adapter.booking_availability(search_request)

    def booking(self, book_request: HotelBookingRequest):
        adapter = self._get_adapters(book_request.crs)[0]
        return adapter.booking(book_request)

    @staticmethod
    def _get_adapters(crs_name):
        if crs_name is None:
            return [HOTEL_ADAPTERS.get("stub")]
        else:
            return [HOTEL_ADAPTERS.get(x) for x in crs_name.split(",")]
