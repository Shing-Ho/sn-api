from decimal import Decimal, ROUND_UP, getcontext
from typing import List, Union, Tuple, Callable, Optional

from api import logger
from api.hotel.models.hotel_common_models import RoomRate
from api.hotel import markups, hotel_cache_service, hotel_mappings
from api.hotel.adapters import adapter_service
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.models.hotel_api_model import (
    HotelDetails,
    HotelSpecificSearch,
    AdapterHotel,
    HotelLocationSearch,
    HotelDetailsSearchRequest,
    Hotel,
    BaseHotelSearch,
    Image,
    ImageType,
)
from api.hotel.models.adapter_models import AdapterHotelSearch, AdapterOccupancy
from api.models.models import ProviderImages, ProviderMapping
from api.view.exceptions import SimplenightApiException, AvailabilityException, AvailabilityErrorCode


def search_by_location(search_request: HotelLocationSearch) -> List[Hotel]:
    all_hotels = _search_all_adapters(search_request, HotelAdapter.search_by_location)
    return _process_hotels(all_hotels)


def search_by_id(search_request: HotelSpecificSearch) -> Hotel:
    adapters_to_search = adapter_service.get_adapters_to_search(search_request)
    adapters = adapter_service.get_adapters(adapters_to_search)

    adapter_search_request = _adapter_search_request(search_request, adapters[0].get_provider_name())

    if len(adapters) > 1:
        raise SimplenightApiException("More than one adapter specified in hotel specific search", 500)

    hotel = adapters[0].search_by_id(adapter_search_request)
    return _process_hotels(hotel)


def details(hotel_details_req: HotelDetailsSearchRequest) -> HotelDetails:
    adapter = adapter_service.get_adapters(hotel_details_req.provider)[0]
    return adapter.details(hotel_details_req)


def recheck(provider: str, room_rate: RoomRate) -> RoomRate:
    adapter = adapter_service.get_adapter(provider)
    return adapter.recheck(room_rate)


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
        return _process_hotel(adapter_hotels)

    return list(filter(lambda x: x is not None, map(_process_hotel, adapter_hotels)))


def _process_hotel(adapter_hotel: AdapterHotel) -> Optional[Hotel]:
    simplenight_hotel_id = hotel_mappings.find_simplenight_hotel_id(
        provider_hotel_id=adapter_hotel.hotel_id, provider_name=adapter_hotel.provider
    )

    if not simplenight_hotel_id:
        logger.warn(f"Skipping {adapter_hotel.provider} hotel {adapter_hotel.hotel_id} because no SN mapping found")
        return None

    _markup_room_rates(adapter_hotel)
    _enrich_hotels(adapter_hotel)
    average_nightly_base, average_nightly_tax, average_nightly_rate = _calculate_hotel_min_nightly_rates(adapter_hotel)

    return Hotel(
        hotel_id=simplenight_hotel_id,
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


def _enrich_hotels(adapter_hotel: AdapterHotel):
    provider_name = adapter_hotel.provider
    provider_code = adapter_hotel.hotel_id
    try:
        provider_mapping = _get_provider_mapping(provider_name, provider_code=provider_code)
        _enrich_images(adapter_hotel, provider_mapping)
    except Exception:
        logger.exception("Error while enriching hotel")


def _enrich_images(adapter_hotel: AdapterHotel, provider_mapping: ProviderMapping):
    if not provider_mapping:
        return

    iceportal_images = _get_iceportal_images_from_provider_code(provider_mapping)
    if iceportal_images:
        iceportal_images = list(map(_convert_image, iceportal_images))
        adapter_hotel.hotel_details.thumbnail_url = iceportal_images[0]
        adapter_hotel.hotel_details.photos = iceportal_images


def _get_iceportal_images_from_provider_code(provider_mapping: ProviderMapping):
    iceportal_mapping = _get_provider_mapping("iceportal", giata_code=provider_mapping.giata_code)

    if not iceportal_mapping:
        return []

    images = ProviderImages.objects.filter(provider__name="iceportal", provider_code=iceportal_mapping.provider_code)
    images.order_by("display_order")

    return images


def _get_provider_mapping(provider_name, provider_code=None, giata_code=None):
    try:
        if giata_code:
            provider_mapping = ProviderMapping.objects.get(provider__name=provider_name, giata_code=giata_code)
        elif provider_code:
            provider_mapping = ProviderMapping.objects.get(provider__name=provider_name, provider_code=provider_code)
        else:
            raise ValueError("Must provide provider_code or giata_code")

        logger.info(f"Found provider mapping: {provider_mapping}")
        return provider_mapping
    except ProviderMapping.DoesNotExist:
        logger.info(f"Could not find mapping info for provider hotel: {provider_name}/{provider_code}")


def _convert_image(provider_image: ProviderImages):
    return Image(url=provider_image.image_url, type=ImageType.UNKNOWN, display_order=provider_image.display_order)


def _markup_room_rates(hotel: AdapterHotel):
    room_rates = []
    for provider_rate in hotel.room_rates:
        simplenight_rate = markups.markup_rate(provider_rate)
        hotel_cache_service.save_provider_rate_in_cache(hotel, provider_rate, simplenight_rate)
        room_rates.append(simplenight_rate)

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


def _adapter_search_request(search: HotelSpecificSearch, provider_name: str) -> AdapterHotelSearch:
    provider_hotel_id = hotel_mappings.find_provider_hotel_id(search.hotel_id, provider_name)
    if not provider_hotel_id:
        raise AvailabilityException(
            detail="Provider hotel mapping not found", error_type=AvailabilityErrorCode.HOTEL_NOT_FOUND
        )

    occupancy = AdapterOccupancy(
        adults=search.occupancy.adults, children=search.occupancy.children, num_rooms=search.occupancy.num_rooms
    )

    return AdapterHotelSearch(
        start_date=search.start_date,
        end_date=search.end_date,
        occupancy=occupancy,
        language=search.language,
        currency=search.currency,
        provider_hotel_id=provider_hotel_id,
        simplenight_hotel_id=search.hotel_id,
    )
