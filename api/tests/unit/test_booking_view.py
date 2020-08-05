from datetime import date

import requests_mock

from api.common.models import RoomOccupancy
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.hotel_model import HotelLocationSearch, Hotel
from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase
from api.tests.utils import load_test_resource

BOOKING_ENDPOINT = "/api/v1/hotels/booking/"
SEARCH_BY_LOCATION = "/api/v1/hotels/search-by-location/"


class TestBookingView(SimplenightAPITestCase):
    def test_hotelbeds_availability(self):
        hotelbeds_location_response = load_test_resource("hotelbeds/search-by-location-response.json")
        hotelbeds_content_response = load_test_resource("hotelbeds/hotel-details-response.json")

        search_request = HotelLocationSearch(
            location_name="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            crs="hotelbeds",
        )

        with requests_mock.Mocker() as mocker:
            mocker.post(HotelBedsTransport.get_hotels_url(), text=hotelbeds_location_response)
            mocker.get(HotelBedsTransport.get_hotel_content_url(), text=hotelbeds_content_response)
            response = self.post(SEARCH_BY_LOCATION, search_request)

        hotels = Hotel.Schema(many=True).load(response.data)
        assert len(hotels) == 24

    def test_hotelbeds_booking(self):
        pass
