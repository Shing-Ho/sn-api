import unittest
from datetime import date

from api.hotel.adapters import hotel_service
from api.hotel.hotel_model import HotelSpecificSearch, RoomOccupancy, HotelLocationSearch


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
            crs="stub"
        )

        hotel = hotel_service.search_by_location(search_request)
        print(hotel)
