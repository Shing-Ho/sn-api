from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from api.booking.booking_model import HotelBookingRequest
from api.hotel.adapters import adapter_service
from api.hotel.hotel_model import (
    HotelDetails,
    HotelSpecificSearch,
    HotelSearchResponseHotel,
    HotelLocationSearch,
    HotelDetailsSearchRequest,
    BaseHotelSearch,
)

MAX_WORKERS = 5


def search_by_location(search_request: HotelLocationSearch) -> List[HotelSearchResponseHotel]:
    futures = []
    all_hotels = []

    adapters = adapter_service.get_adapters(search_request.crs)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for adapter in adapters:
            futures.append(executor.submit(adapter.search_by_location, search_request))

        for future in futures:
            all_hotels.extend(future.result())

    return all_hotels


def search_by_id(search_request: HotelSpecificSearch) -> HotelSearchResponseHotel:
    adapter = adapter_service.get_adapters(search_request.crs)[0]
    return adapter.search_by_id(search_request)


def details(hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
    adapter = adapter_service.get_adapters(hotel_details_req.crs)[0]
    return adapter.details(hotel_details_req)


def recheck(crs: str, search: BaseHotelSearch, rate_key: str) -> HotelSearchResponseHotel:
    adapter = adapter_service.get_adapters(crs)[0]
    return adapter.recheck(search, rate_key)


def booking_availability(search_request: HotelSpecificSearch):
    adapter = adapter_service.get_adapters(search_request.crs)[0]
    return adapter.booking_availability(search_request)


def booking(book_request: HotelBookingRequest):
    adapter = adapter_service.get_adapters(book_request.crs)[0]
    return adapter.booking(book_request)
