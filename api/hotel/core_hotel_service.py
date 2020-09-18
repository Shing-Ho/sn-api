from decimal import Decimal, ROUND_UP, getcontext
from typing import List, Union, Tuple, Callable

from api.booking.booking_model import HotelBookingRequest
from api.common.models import RoomRate
from api.hotel import markups, hotel_cache_service
from api.hotel.adapters import adapter_service
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import (
    HotelDetails,
    HotelSpecificSearch,
    AdapterHotel,
    HotelLocationSearch,
    HotelDetailsSearchRequest,
    Hotel,
    BaseHotelSearch,
)
from api.view.exceptions import SimplenightApiException


def search_by_location(search_request: HotelLocationSearch) -> List[Hotel]:
    all_hotels = _search_all_adapters(search_request, HotelAdapter.search_by_location)
    return _process_hotels(all_hotels)


def search_by_id(search_request: HotelSpecificSearch) -> Hotel:
    adapters_to_search = adapter_service.get_adapters_to_search(search_request)
    adapters = adapter_service.get_adapters(adapters_to_search)

    if len(adapters) > 1:
        raise SimplenightApiException("More than one adapter specified in hotel specific search", 500)

    hotel = adapters[0].search_by_id(search_request)
    return _process_hotels(hotel)


def details(hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
    adapter = adapter_service.get_adapters(hotel_details_req.provider)[0]
    return adapter.details(hotel_details_req)


def recheck(provider: str, room_rate: RoomRate) -> RoomRate:
    adapter = adapter_service.get_adapter(provider)
    return adapter.recheck(room_rate)


def booking(book_request: HotelBookingRequest):
    adapter = adapter_service.get_adapters(book_request.provider)[0]
    return adapter.booking(book_request)


def _search_all_adapters(search_request: BaseHotelSearch, adapter_fn: Callable):
    adapters_to_search = adapter_service.get_adapters_to_search(search_request)
    adapters = adapter_service.get_adapters(adapters_to_search)

    hotels = []
    for adapter in adapters:
        adapter_fn_name = getattr(adapter, adapter_fn.__name__)
        hotels.extend(adapter_fn_name(search_request))

    return hotels


def _process_hotels(adapter_hotels: Union[List[AdapterHotel], AdapterHotel]) -> Union[Hotel, List[Hotel]]:
    """
    Given an AdapterHotel, calculate markups, minimum nightly rates
    and return a Hotel object suitable for the API view layer
    """

    if isinstance(adapter_hotels, AdapterHotel):
        return __process_hotels(adapter_hotels)

    return list(map(__process_hotels, adapter_hotels))


def __process_hotels(adapter_hotel: AdapterHotel) -> Hotel:
    _markup_room_rates(adapter_hotel)
    average_nightly_base, average_nightly_tax, average_nightly_rate = _calculate_hotel_min_nightly_rates(adapter_hotel)

    return Hotel(
        hotel_id=adapter_hotel.hotel_id,
        start_date=adapter_hotel.start_date,
        end_date=adapter_hotel.end_date,
        occupancy=adapter_hotel.occupancy,
        hotel_details=adapter_hotel.hotel_details,
        room_types=adapter_hotel.room_types,
        room_rates=adapter_hotel.room_rates,
        rate_plans=adapter_hotel.rate_plans,
        average_nightly_rate=average_nightly_rate,
        average_nightly_base=average_nightly_base,
        average_nightly_tax=average_nightly_tax,
    )


def _markup_room_rates(hotel: AdapterHotel):
    room_rates = []
    for provider_rate in hotel.room_rates:
        markup_rate = markups.markup_rate(provider_rate)
        hotel_cache_service.save_provider_rate_in_cache(hotel, provider_rate, markup_rate)
        room_rates.append(markup_rate)

    hotel.room_rates = room_rates


def _get_nightly_rate(hotel: Union[Hotel, AdapterHotel], amount: Decimal):
    room_nights = max((hotel.end_date - hotel.start_date).days, 1)

    getcontext().rounding = ROUND_UP
    return Decimal(round(amount / room_nights, 2))


def _calculate_hotel_min_nightly_rates(hotel: Union[Hotel, AdapterHotel]) -> Tuple[Decimal, Decimal, Decimal]:
    least_cost_rate = min(hotel.room_rates, key=lambda x: x.total.amount)

    min_nightly_total = _get_nightly_rate(hotel, least_cost_rate.total.amount)
    min_nightly_tax = _get_nightly_rate(hotel, least_cost_rate.total_tax_rate.amount)
    min_nightly_base = _get_nightly_rate(hotel, least_cost_rate.total_base_rate.amount)

    return min_nightly_base, min_nightly_tax, min_nightly_total
