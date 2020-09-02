from typing import List

from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.adapters.travelport.transport import TravelportTransport
from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.hotel.hotel_adapter import HotelAdapter

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
