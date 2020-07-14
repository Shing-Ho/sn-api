import unittest
from datetime import date

from api.hotel.adapters.hotel_service import HotelService
from api.hotel.hotels import HotelSpecificSearch, RoomOccupancy


class TestHotelService(unittest.TestCase):
    def test_search_by_hotel_id(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
        )

        hotel_service = HotelService(adapters="stub")
        hotel = hotel_service.search_by_id(search_request)
        print(hotel)
