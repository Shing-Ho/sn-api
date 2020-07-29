import unittest
import uuid
from datetime import date

from api.hotel import translate
from api.hotel.adapters import hotel_service
from api.hotel.hotel_model import HotelSpecificSearch, RoomOccupancy, HotelLocationSearch
from api.hotel.translate.google import GoogleHotelSearchRequest, GoogleHotelApiResponse
from api.hotel.translate.google_models import RoomParty


class TestHotelService(unittest.TestCase):
    def test_search_by_hotel_id(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            crs="stub",
        )

        hotel = hotel_service.search_by_id(search_request)
        print(hotel)

    def test_search_by_location(self):
        search_request = HotelLocationSearch(
            location_name="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            crs="stub",
        )

        hotel = hotel_service.search_by_location(search_request)
        print(hotel)

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
        google_hotel = translate.google.translate_hotel_response(google_search_request, hotel)

        print(GoogleHotelApiResponse.Schema().dumps(google_hotel, indent=2))
