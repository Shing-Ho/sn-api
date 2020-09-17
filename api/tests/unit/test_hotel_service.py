from datetime import date

from django.test import TestCase

from api.hotel import hotel_service
from api.hotel.hotel_model import HotelSpecificSearch, RoomOccupancy, HotelLocationSearch, SimplenightHotel


class TestHotelService(TestCase):
    def test_search_by_hotel_id(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            provider="stub",
        )

        hotel = hotel_service.search_by_id(search_request)
        self.assertIsNotNone(hotel)
        self.assertTrue(isinstance(hotel, SimplenightHotel))

    def test_search_by_location(self):
        search_request = HotelLocationSearch(
            location_id="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            provider="stub",
        )

        hotel = hotel_service.search_by_location(search_request)
        self.assertIsNotNone(hotel)
        self.assertEqual("2020-01-20", str(hotel[0].start_date))
        self.assertEqual("2020-01-27", str(hotel[0].end_date))
        self.assertTrue(len(hotel[0].hotel_details.amenities) >= 3)
        self.assertTrue(isinstance(hotel[0], SimplenightHotel))
