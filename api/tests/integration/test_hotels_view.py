from datetime import datetime, timedelta
from typing import List

from api.hotel.hotels import HotelSpecificSearch, RoomOccupancy, HotelSearchResponseHotel, HotelLocationSearch
from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase

SEARCH_BY_ID = "/api/v1/hotels/search-by-id/"
SEARCH_BY_LOCATION = "/api/v1/hotels/search-by-location/"


class TestHotelsView(SimplenightAPITestCase):
    def test_search_by_id(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)

        search = HotelSpecificSearch(start_date=checkin, end_date=checkout, occupancy=RoomOccupancy(adults=1))
        request_data = HotelSpecificSearch.Schema().dump(search)

        response = self.client.post(path=SEARCH_BY_ID, data=request_data, format="json")

        self.assertEqual(200, response.status_code)

        hotel: HotelSearchResponseHotel = HotelSearchResponseHotel.Schema().load(response.json())

        self.assertIsNotNone(hotel.hotel_id)

    def test_search_by_location(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=RoomOccupancy(adults=1), location_name="SFO"
        )

        request_data = HotelLocationSearch.Schema().dump(search)

        response = self.client.post(path=SEARCH_BY_LOCATION, data=request_data, format="json")

        self.assertEqual(200, response.status_code)

        hotels: List[HotelSearchResponseHotel] = HotelSearchResponseHotel.Schema(many=True).load(response.json())
        self.assertTrue(len(hotels) > 1)
        self.assertIsNotNone(hotels[0].hotel_id)

    def test_search_location_by_crs(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin,
            end_date=checkout,
            occupancy=RoomOccupancy(adults=1),
            location_name="SFO",
            crs="hotelbeds,stub",
        )

        request_data = HotelLocationSearch.Schema().dump(search)

        response = self.client.post(path=SEARCH_BY_LOCATION, data=request_data, format="json")

        self.assertEqual(200, response.status_code)

        hotels: List[HotelSearchResponseHotel] = HotelSearchResponseHotel.Schema(many=True).load(response.json())
        self.assertTrue(len(hotels) > 1)
        self.assertIsNotNone(hotels[0].hotel_id)

        print(hotels)