from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Union

from api.booking.booking_model import HotelBookingRequest
from api.common import cache_storage
from api.common.models import RoomRate
from api.hotel import markups
from api.hotel.adapters import adapter_service
from api.hotel.hotel_model import (
    HotelDetails,
    HotelSpecificSearch,
    CrsHotel,
    HotelLocationSearch,
    HotelDetailsSearchRequest,
)

MAX_WORKERS = 5


def search_by_location(search_request: HotelLocationSearch) -> List[CrsHotel]:
    futures = []
    all_hotels = []

    adapters = adapter_service.get_adapters(search_request.crs)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for adapter in adapters:
            futures.append(executor.submit(adapter.search_by_location, search_request))

        for future in futures:
            all_hotels.extend(future.result())

    process_hotels(all_hotels)
    return all_hotels


def search_by_id(search_request: HotelSpecificSearch) -> CrsHotel:
    adapter = adapter_service.get_adapters(search_request.crs)[0]
    hotel = adapter.search_by_id(search_request)
    process_hotels(hotel)

    return hotel


def details(hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
    adapter = adapter_service.get_adapters(hotel_details_req.crs)[0]
    return adapter.details(hotel_details_req)


def recheck(crs: str, room_rate: List[RoomRate]) -> List[RoomRate]:
    adapter = adapter_service.get_adapters(crs)[0]
    return adapter.recheck(room_rate)


def booking(book_request: HotelBookingRequest):
    adapter = adapter_service.get_adapters(book_request.crs)[0]
    return adapter.booking(book_request)


def process_hotels(hotels: Union[List[CrsHotel], CrsHotel]):
    if isinstance(hotels, CrsHotel):
        hotels = [hotels]

    for hotel in hotels:
        markup_room_rates(hotel)


def markup_room_rates(hotel: CrsHotel):
    for room_type in hotel.room_types:
        room_rates = []

        for crs_rate in room_type.rates:
            markup_rate = markups.markup_rate(crs_rate)
            cache_storage.set(markup_rate.rate_key, crs_rate)
            room_rates.append(markup_rate)

        room_type.rates = room_rates

