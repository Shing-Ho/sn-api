import json
import unittest
from datetime import datetime
from datetime import timedelta

import zeep

from api.hotel.hotels import HotelSearchRequest
from api.hotel.travelport import TravelportHotelAdapter
from api.tests import utils


class TestTravelport(unittest.TestCase):
    def test_search(self):
        travelport = TravelportHotelAdapter()

        checkin_date = datetime.now().date() + timedelta(days=30)
        checkout_date = datetime.now().date() + timedelta(days=37)
        search_request = HotelSearchRequest(location_name="SFO", checkin_date=checkin_date, checkout_date=checkout_date)

        results = travelport.search(search_request)
        print(results)

    def test_hotel_details(self):
        travelport = TravelportHotelAdapter()

        checkin_date = datetime.now().date() + timedelta(days=30)
        checkout_date = datetime.now().date() + timedelta(days=37)
        chain_code = "LQ"
        hotel_code = "17352"

        response = travelport.details(chain_code, hotel_code, checkin_date, checkout_date)
        print(json.dumps(zeep.helpers.serialize_object(response), indent=2))
