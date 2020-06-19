from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.adapters.travelport.transport import TravelportTransport
from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotels import (
    HotelDetails,
    HotelSpecificSearch,
    HotelSearchResponse,
    HotelLocationSearch,
    HotelAdapterHotel,
    HotelDetailsSearchRequest,
)

HOTEL_ADAPTERS = {"stub": StubHotelAdapter(), "travelport": TravelportHotelAdapter(TravelportTransport())}


class HotelService(HotelAdapter):
    MAX_WORKERS = 5

    def __init__(self, adapters):
        self.adapters = adapters

    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelAdapterHotel]:
        futures = []
        all_hotels = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            for adapter in self.adapters:
                futures.append(executor.submit(HOTEL_ADAPTERS[adapter].search_by_location, search_request))

            for future in futures:
                all_hotels.extend(future.result())

        return all_hotels

    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponse:
        return HOTEL_ADAPTERS[self.adapters].search_by_id(search_request)

    def details(self, hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
        return HOTEL_ADAPTERS.get(self.adapters).details(hotel_details_req)
