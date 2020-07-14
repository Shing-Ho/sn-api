from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.adapters.travelport.transport import TravelportTransport
from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotels import (
    HotelDetails,
    HotelSpecificSearch,
    HotelSearchResponseHotel,
    HotelLocationSearch,
    HotelAdapterHotel,
    HotelDetailsSearchRequest, HotelBookingRequest,
)

HOTEL_ADAPTERS = {"stub": StubHotelAdapter(), "travelport": TravelportHotelAdapter(TravelportTransport())}


class HotelService(HotelAdapter):
    MAX_WORKERS = 5

    def __init__(self, adapters):
        self.adapters = adapters

    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelSearchResponseHotel]:
        futures = []
        all_hotels = []

        # TODO: Re-add support for multiple adapters
        adapters = {self.adapters}
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            for adapter in adapters:
                futures.append(executor.submit(HOTEL_ADAPTERS[adapter].search_by_location, search_request))

            for future in futures:
                all_hotels.extend(future.result())

        return all_hotels

    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponseHotel:
        return self.get_adapter().search_by_id(search_request)

    def details(self, hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
        return self.get_adapter().details(hotel_details_req)

    def booking_availability(self, search_request: HotelSpecificSearch):
        return self.get_adapter().booking_availability(search_request)

    def booking(self, book_request: HotelBookingRequest):
        return self.get_adapter().booking(book_request)

    def get_adapter(self):
        return HOTEL_ADAPTERS.get(self.adapters)
