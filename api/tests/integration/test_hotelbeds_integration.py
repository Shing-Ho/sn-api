import unittest
from datetime import datetime, timedelta

from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.hotels import HotelLocationSearch


class TestHotelBedsIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.hotelbeds = HotelBeds()

    def test_location_search(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search_request = HotelLocationSearch(
            location_name="TVL", checkin_date=checkin, checkout_date=checkout, daily_rates=True
        )

        response = self.hotelbeds._search_by_location(search_request)
        print(response)

    def test_hotel_details(self):
        hotel_codes = ["349168", "97334"]
        response = self.hotelbeds.details(hotel_codes, "en_US")
        print(response)