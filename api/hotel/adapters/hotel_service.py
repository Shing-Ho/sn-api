from concurrent.futures.thread import ThreadPoolExecutor
from decimal import Decimal
from typing import List, Union, Tuple

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
    HotelDetailsSearchRequest, Hotel,
)

MAX_WORKERS = 5


def search_by_location(search_request: HotelLocationSearch) -> List[Hotel]:
    futures = []
    all_hotels = []

    adapters = adapter_service.get_adapters(search_request.crs)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for adapter in adapters:
            futures.append(executor.submit(adapter.search_by_location, search_request))

        for future in futures:
            all_hotels.extend(future.result())

    return _process_hotels(all_hotels)


def search_by_id(search_request: HotelSpecificSearch) -> Hotel:
    adapter = adapter_service.get_adapters(search_request.crs)[0]
    hotel = adapter.search_by_id(search_request)
    return _process_hotels(hotel)


def details(hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
    adapter = adapter_service.get_adapters(hotel_details_req.crs)[0]
    return adapter.details(hotel_details_req)


def recheck(crs: str, room_rate: List[RoomRate]) -> List[RoomRate]:
    adapter = adapter_service.get_adapters(crs)[0]
    return adapter.recheck(room_rate)


def booking(book_request: HotelBookingRequest):
    adapter = adapter_service.get_adapters(book_request.crs)[0]
    return adapter.booking(book_request)


def _process_hotels(crs_hotels: Union[List[CrsHotel], CrsHotel]) -> Union[Hotel, List[Hotel]]:
    if isinstance(crs_hotels, CrsHotel):
        return _calculate_and_convert_hotel(crs_hotels)

    return list(map(_calculate_and_convert_hotel, crs_hotels))



def _calculate_and_convert_hotel(crs_hotel: CrsHotel) -> Hotel:
    """Given a CRS Hotel, calculate markups, mininimum nightly rates
    and return a Hotel object suitable for the API view layer
    """

    _markup_room_rates(crs_hotel)
    average_nightly_base, average_nightly_tax, average_nightly_rate = _calculate_min_nightly_rates(crs_hotel)
    return Hotel(
        hotel_id=crs_hotel.hotel_id,
        start_date=crs_hotel.start_date,
        end_date=crs_hotel.end_date,
        occupancy=crs_hotel.occupancy,
        hotel_details=crs_hotel.hotel_details,
        room_types=crs_hotel.room_types,
        average_nightly_rate=average_nightly_rate,
        average_nightly_base=average_nightly_base,
        average_nightly_tax=average_nightly_tax
    )


def _markup_room_rates(hotel: CrsHotel):
    for room_type in hotel.room_types:
        room_rates = []

        for crs_rate in room_type.rates:
            markup_rate = markups.markup_rate(crs_rate)
            cache_storage.set(markup_rate.rate_key, crs_rate)
            room_rates.append(markup_rate)

        room_type.rates = room_rates


def _calculate_min_nightly_rates(hotel: CrsHotel) -> Tuple[Decimal, Decimal, Decimal]:
    rates = [rate for room_type in hotel.room_types for rate in room_type.rates]
    room_nights = max((hotel.end_date - hotel.start_date).days, 1)

    least_cost_rate = min(rates, key=lambda x: x.total.amount)

    def get_nightly_rate(amount: Decimal):
        return Decimal(round(amount / room_nights, 2))

    min_nightly_total = get_nightly_rate(least_cost_rate.total.amount)
    min_nightly_tax = get_nightly_rate(least_cost_rate.total_tax_rate.amount)
    min_nightly_base = get_nightly_rate(least_cost_rate.total_base_rate.amount)

    return min_nightly_base, min_nightly_tax, min_nightly_total
