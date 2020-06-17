from typing import List, Optional

from api.hotel.hotels import (
    HotelAdapter,
    HotelSearchRequest,
    HotelAdapterHotel,
    HotelAddress,
    HotelRate,
    HotelDetailsSearchRequest
)
from api.hotel.travelport.hotel_details import TravelportHotelDetailsBuilder
from api.hotel.travelport.search import TravelportHotelSearchBuilder
from api.hotel.travelport.transport import TravelportTransport


class TravelportHotelAdapter(HotelAdapter):
    def __init__(self, transport: TravelportTransport = None):
        if transport is None:
            self.transport = TravelportTransport()

    def search(self, search_request: HotelSearchRequest) -> List[HotelAdapterHotel]:
        hotel_search_service = self.transport.create_hotel_search_service()
        request = TravelportHotelSearchBuilder().build(search_request)
        response = hotel_search_service.service(**request)

        hotel_response = response["HotelSuperShopperResults"]
        hotels_with_rates = filter(lambda x: x["HotelRateDetail"], hotel_response)
        return list(map(self._hotel_from_response, hotels_with_rates))

    def details(self, hotel_details: HotelDetailsSearchRequest):
        hotel_details_service = self.transport.create_hotel_details_service()
        request = TravelportHotelDetailsBuilder.build(hotel_details)
        response = hotel_details_service.service(**request)

        return response

    @classmethod
    def _hotel_from_response(cls, hotel):
        hotel_property = hotel["HotelProperty"]
        tax, total = cls._parse_hotel_min_max_rate(hotel)

        address, city, state, postal_code, country = hotel_property["PropertyAddress"]["Address"]
        address = HotelAddress(city, state, postal_code, country, [address])

        chain = hotel_property["HotelChain"]
        name = hotel_property["Name"]

        hotel_rate = HotelRate(total, tax)
        star_rating = cls._parse_hotel_star_rating(hotel_property)

        return HotelAdapterHotel(name, chain, address, hotel_rate, star_rating)

    @staticmethod
    def _parse_hotel_star_rating(hotel) -> Optional[int]:
        return next(map(lambda x: x.Rating, hotel["HotelRating"]), None)

    @staticmethod
    def _parse_hotel_min_max_rate(hotel):
        rate = hotel["HotelRateDetail"]
        rate = rate[0]
        total = rate["Total"][3:]
        if rate["Tax"]:
            tax = rate["Tax"][3:]
        else:
            tax = 0.00
        return tax, total
