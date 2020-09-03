from typing import List

from api.auth.models import Feature
from api.common.request_context import get_request_context
from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.adapters.travelport.transport import TravelportTransport
from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import BaseHotelSearch

HOTEL_ADAPTERS = {
    "stub": StubHotelAdapter(),
    "travelport": TravelportHotelAdapter(TravelportTransport()),
    "hotelbeds": HotelBeds(HotelBedsTransport()),
    "priceline": PricelineAdapter(PricelineTransport(test_mode=True)),
}


def get_adapter(crs_name):
    return HOTEL_ADAPTERS.get(crs_name)


def get_adapters(crs_name) -> List[HotelAdapter]:
    if crs_name is None:
        return [HOTEL_ADAPTERS.get("stub")]
    else:
        return [HOTEL_ADAPTERS.get(x) for x in crs_name.split(",")]


def get_adapters_to_search(search_request: BaseHotelSearch) -> str:
    """
    Returns a list of adapters to search, identified by their string name.
    If an adapter is explicitly specified in the request, return that.
    Otherwise, return the list of adapters enabled for a particular organization, if an
    organization is associated with the request (by API key).

    If no organization is associated, return the stub adapter.
    """

    if search_request.crs:
        return search_request.crs

    organization = get_request_context().get_organization()
    if organization:
        organization_enabled_adapters = organization.get_feature(Feature.ENABLED_ADAPTERS)
        if organization_enabled_adapters:
            return organization_enabled_adapters

    return "stub"
