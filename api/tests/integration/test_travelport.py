import unittest
from datetime import datetime, timedelta

from api.hotel.hotels import HotelSearchRequest
from api.hotel.travelport import TravelportHotelAdapter


class TestTravelport(unittest.TestCase):
    def test_search(self):
        travelport = TravelportHotelAdapter()

        checkin_date = datetime.now().date() + timedelta(days=30)
        checkout_date = datetime.now().date() + timedelta(days=37)
        search_request = HotelSearchRequest(location_name="SFO", checkin_date=checkin_date, checkout_date=checkout_date)

        results = travelport.search(search_request)
        print(results)
