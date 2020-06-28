from typing import List

from api.hotel.adapters.hotelbeds.search import HotelBedsSearchBuilder, HotelBedsAvailabilityRS
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotels import (
    HotelBookingRequest,
    HotelSpecificSearch,
    HotelDetails,
    HotelSearchResponse,
    HotelLocationSearch, HotelAdapterHotel
)


class HotelBeds(HotelAdapter):
    def __init__(self, transport=None):
        if transport is None:
            transport = HotelBedsTransport()

        self.transport = transport

    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelAdapterHotel]:
        results = self._search_by_location(search_request)

        return []

    def _search_by_location(self, search_request: HotelLocationSearch) -> HotelBedsAvailabilityRS:
        request = HotelBedsSearchBuilder.build(search_request)
        endpoint = self.transport.get_hotels_url()
        response = self.transport.submit(endpoint, request)

        if response.ok:
            return HotelBedsAvailabilityRS.Schema().load(response.json())

    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponse:
        pass

    def details(self, *args) -> HotelDetails:
        pass

    def booking_availability(self, search_request: HotelSpecificSearch):
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass