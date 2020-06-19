import unittest
from datetime import date

from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.hotels import HotelSpecificSearch, RoomOccupancy, HotelSearchResponse


class TestStubHotelAdapter(unittest.TestCase):
    def test_search_by_hotel_id(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            checkin_date=date(2020, 1, 20),
            checkout_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
        )

        stub_adapter = StubHotelAdapter()
        response = stub_adapter.search_by_id(search_request)
        print(HotelSearchResponse.Schema().dumps(response))