import unittest
from datetime import datetime, timedelta

from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.hotels import HotelLocationSearch


class TestHotelBedsIntegration(unittest.TestCase):
    def test_location_search(self):
        hotelbeds = HotelBeds()

        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)

        search_request = HotelLocationSearch(location_name="TVL", checkin_date=checkin, checkout_date=checkout)
        response = hotelbeds.search_by_location(search_request)
        print(response)