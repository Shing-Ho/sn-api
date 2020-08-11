import uuid
from datetime import date

from django.test import TestCase

from api.common import cache_storage
from api.common.models import RoomRate
from api.hotel import converter
from api.hotel.adapters import hotel_service
from api.hotel.converter.google import GoogleHotelSearchRequest
from api.hotel.converter.google_models import RoomParty
from api.hotel.hotel_model import HotelSpecificSearch, RoomOccupancy, HotelLocationSearch


class TestHotelService(TestCase):
    def test_search_by_hotel_id(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            crs="stub",
        )

        hotel = hotel_service.search_by_id(search_request)
        self.assertIsNotNone(hotel)

    def test_search_by_location(self):
        search_request = HotelLocationSearch(
            location_name="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            crs="stub",
        )

        hotel = hotel_service.search_by_location(search_request)
        self.assertIsNotNone(hotel)

    def test_search_by_hotel_id_google(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            crs="stub",
        )

        google_search_request = GoogleHotelSearchRequest(
            api_version=1,
            transaction_id=str(uuid.uuid4()),
            hotel_id=search_request.hotel_id,
            start_date=search_request.start_date,
            end_date=search_request.end_date,
            party=RoomParty(adults=search_request.occupancy.adults, children=[]),
        )

        hotel = hotel_service.search_by_id(search_request)
        google_hotel = converter.google.convert_hotel_response(google_search_request, hotel)

        self.assertIsNotNone(google_hotel)

    def test_markups_applied_and_stored_in_cache(self):
        search_request = HotelLocationSearch(
            location_name="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            crs="stub",
        )

        hotels = hotel_service.search_by_location(search_request)

        room_rates = [x for hotel in hotels for room_type in hotel.room_types for x in room_type.rates]
        assert len(room_rates) > 10

        for room_rate in room_rates:
            crs_rate: RoomRate = cache_storage.get(room_rate.rate_key)
            assert crs_rate is not None
            assert crs_rate.total.amount < room_rate.total.amount
