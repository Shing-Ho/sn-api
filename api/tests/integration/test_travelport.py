import unittest
from datetime import datetime
from datetime import timedelta

from api.hotel.hotels import HotelSearchRequest, HotelDetailsSearchRequest
from api.hotel.travelport.travelport import TravelportHotelAdapter


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
        hotel_details = HotelDetailsSearchRequest(
            chain_code="HY",
            hotel_code="09974",
            checkin_date=datetime.now().date() + timedelta(days=30),
            checkout_date=datetime.now().date() + timedelta(days=37),

        )

        response = travelport.details(hotel_details)
        print(response)
