from datetime import datetime, timedelta, date
from typing import List

import requests_mock

from api.common.models import to_json
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.hotel_model import (
    HotelSpecificSearch,
    RoomOccupancy,
    HotelLocationSearch, Hotel,
)
from api.tests import test_objects
from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase
from api.tests.utils import load_test_resource

SEARCH_BY_ID = "/api/v1/hotels/search-by-id"
SEARCH_BY_LOCATION = "/api/v1/hotels/search-by-location"
BOOKING = "/api/v1/hotels/booking"


class TestHotelsView(SimplenightAPITestCase):
    def test_search_by_id(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)

        search = HotelSpecificSearch(start_date=checkin, end_date=checkout, occupancy=RoomOccupancy(adults=1))
        response = self._post(SEARCH_BY_ID, search)
        self.assertEqual(200, response.status_code)

        hotel: Hotel = Hotel.Schema().load(response.json())

        self.assertIsNotNone(hotel.hotel_id)

    def test_search_by_location(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=RoomOccupancy(adults=1), location_name="SFO"
        )

        response = self._post(SEARCH_BY_LOCATION, search)
        self.assertEqual(200, response.status_code)

        hotels: List[Hotel] = Hotel.Schema(many=True).load(response.json())
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
            crs="hotelbeds",
        )

        response = self._post(SEARCH_BY_LOCATION, search)
        self.assertEqual(200, response.status_code)

        hotels: List[Hotel] = Hotel.Schema(many=True).load(response.json())
        self.assertTrue(len(hotels) > 1)
        self.assertIsNotNone(hotels[0].hotel_id)

    def test_booking_invalid_payment(self):
        invalid_card_number_payment = test_objects.payment("4000000000000002")
        booking_request = test_objects.booking_request(payment_obj=invalid_card_number_payment)

        response = self.post(endpoint=BOOKING, obj=booking_request)

        self.assertEqual(500, response.status_code)
        self.assertIn("error", response.json())
        self.assertIn("Your card was declined", response.json()["error"]["message"])
        self.assertEqual("PAYMENT_DECLINED", response.json()["error"]["type"])
        print(response.json())

    def test_availability_error_included_in_api_rest(self):
        error_response = load_test_resource("hotelbeds/error-response.json")
        with requests_mock.Mocker() as mocker:
            mocker.post(HotelBedsTransport.get_hotels_url(), text=error_response)
            search_request = HotelLocationSearch(
                location_name="SFO",
                start_date=date(2020, 1, 20),
                end_date=date(2020, 1, 27),
                occupancy=RoomOccupancy(2, 1),
                crs="hotelbeds",
            )

            response = self.post(endpoint=SEARCH_BY_LOCATION, obj=search_request)
            body = response.json()
            assert body is not None
            assert body["detail"] == "Invalid data. The check-in must be in the future."
            assert body["status_code"] == 500

    def _post(self, endpoint, data):
        return self.client.post(path=endpoint, data=to_json(data), format="json")
