from datetime import timedelta
from typing import Union

from api import logger
from api.hotel import hotel_service
from api.hotel.google_pricing import google_pricing_serializer
from api.hotel.google_pricing.google_pricing_models import GooglePricingItineraryQuery
from api.hotel.models.hotel_api_model import HotelBatchSearch
from api.hotel.models.hotel_common_models import RoomOccupancy
from api.models.models import ProviderHotel
from api.view.exceptions import AvailabilityException, AvailabilityErrorCode


def live_pricing_api(query: Union[str, bytes, GooglePricingItineraryQuery]) -> str:
    if isinstance(query, (str, bytes)):
        query = google_pricing_serializer.deserialize(query)

    checkout = query.checkin + timedelta(days=query.nights)
    occupancy = RoomOccupancy(adults=1)
    search = HotelBatchSearch(
        start_date=query.checkin, end_date=checkout, occupancy=occupancy, hotel_ids=query.hotel_codes, currency="USD"
    )

    hotels = hotel_service.search_by_id_batch(search)
    if not hotels:
        raise AvailabilityException("Could not find hotels", AvailabilityErrorCode.HOTEL_NOT_FOUND)

    return google_pricing_serializer.serialize(query, hotels)


def generate_property_list(country_codes: str, provider_name="giata"):
    country_codes = country_codes.split(",")
    logger.info(f"Searching for hotels in {country_codes}")

    provider_hotels = ProviderHotel.objects.filter(provider__name=provider_name, country_code__in=country_codes)
    logger.info(f"Found {len(provider_hotels)} hotels")

    return google_pricing_serializer.serialize_property_list(provider_hotels)
