from typing import List, Union

from api import logger
from api.hotel.adapters.hotelbeds.common import get_language_mapping
from api.hotel.adapters.hotelbeds.details import HotelBedsHotelDetailsRS, HotelBedsHotelDetail
from api.hotel.adapters.hotelbeds.search import HotelBedsSearchBuilder, HotelBedsAvailabilityRS, HotelBedsHotel
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotels import (
    HotelBookingRequest,
    HotelSpecificSearch,
    HotelDetails,
    HotelSearchResponse,
    HotelLocationSearch,
    HotelAdapterHotel,
    Address,
)


class HotelBeds(HotelAdapter):
    def __init__(self, transport=None):
        if transport is None:
            transport = HotelBedsTransport()

        self.transport = transport

    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelAdapterHotel]:
        results = self._search_by_location(search_request)

        return []

    def _search_by_location(self, search_request: HotelLocationSearch) -> HotelBedsAvailabilityRS:
        request = HotelBedsSearchBuilder.build(search_request)
        endpoint = self.transport.get_hotels_url()
        response = self.transport.post(endpoint, request)

        if response.ok:
            return HotelBedsAvailabilityRS.Schema().load(response.json())

        logger.error(f"Error searching HotelBeds (status_code={response.status_code}): {response.text}")

    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponse:
        pass

    def details(self, hotel_codes: Union[List[str], str], language: str) -> List[HotelDetails]:
        params = {
            "language": get_language_mapping(language),
            "codes": str.join(",", hotel_codes),
            "fields": "all",
        }

        url = self.transport.get_hotel_content_url()
        response = self.transport.get(url, params)

        if response.ok:
            return HotelBedsHotelDetailsRS.Schema().load(response.json())

        logger.error(f"Error retrieving hotel details (status_code={response.status_code}): {response.text}")

    def booking_availability(self, search_request: HotelSpecificSearch):
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass

    def get_image_url(self, path):
        return self._get_image_base_url() + path

    @staticmethod
    def _get_image_base_url():
        return "http://photos.hotelbeds.com/giata/bigger/"

    def _create_hotel(self, hotel: HotelBedsHotel, detail: HotelBedsHotelDetail) -> HotelAdapterHotel:
        address = Address(
            city=detail.city.content,
            province=detail.state_code,
            postal_code=detail.postal_code,
            country=detail.country_code,
            address1=detail.address.content,
        )

        return HotelAdapterHotel(name=hotel.name, address=address, )
