from typing import List

from api.common.request_context import get_request_context, get_config_bool
from api.hotel.adapters.hotel_adapter import HotelAdapter
from api.hotel.adapters.hotelbeds.hotelbeds_adapter import HotelBeds
from api.hotel.adapters.priceline.priceline_adapter import PricelineAdapter
from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.hotel.models.hotel_api_model import HotelSearch
from api.models.models import Feature

HOTEL_ADAPTERS = {
    "stub": StubHotelAdapter,
    "travelport": TravelportHotelAdapter,
    "hotelbeds": HotelBeds,
    "priceline": PricelineAdapter,
}


def get_adapter(name):
    return HOTEL_ADAPTERS.get(name).factory(get_test_mode())


def get_adapters(name) -> List[HotelAdapter]:
    return [get_adapter(x) for x in name.split(",")]


def get_adapters_to_search(search_request: HotelSearch) -> str:
    """
    Returns a list of adapters to search, identified by their string name.
    If an adapter is explicitly specified in the request, return that.
    Otherwise, return the list of adapters enabled for a particular organization, if an
    organization is associated with the request (by API key).

    If no organization is associated, return the stub adapter.
    """

    if search_request.provider:
        return search_request.provider

    organization = get_request_context().get_organization()
    if organization:
        organization_enabled_adapters = organization.get_feature(Feature.ENABLED_ADAPTERS)
        if organization_enabled_adapters:
            return organization_enabled_adapters

    return "stub"


def get_test_mode():
    return get_config_bool(Feature.TEST_MODE)
