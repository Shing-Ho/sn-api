import unittest
from datetime import datetime
from datetime import timedelta

from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.hotel.hotels import HotelLocationSearch, HotelDetailsSearchRequest


class TestTravelport(unittest.TestCase):
    def test_search(self):
        travelport = TravelportHotelAdapter()

        checkin_date = datetime.now().date() + timedelta(days=30)
        checkout_date = datetime.now().date() + timedelta(days=37)
        search_request = HotelLocationSearch(location_name="SFO", checkin_date=checkin_date, checkout_date=checkout_date)

        results = travelport.search_by_location(search_request)
        print(results)

    def test_hotel_details(self):
        travelport = TravelportHotelAdapter()
        hotel_details = HotelDetailsSearchRequest(
            chain_code="HY",
            hotel_code="09974",
            checkin_date=datetime.now().date() + timedelta(days=30),
            checkout_date=datetime.now().date() + timedelta(days=37),

        )

        response = travelport.details(hotel_details)
        print(response)
