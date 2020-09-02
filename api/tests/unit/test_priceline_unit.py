from datetime import timedelta, datetime

import requests_mock
from django.test import TestCase

from api.common.models import RoomOccupancy
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_model import HotelLocationSearch
from api.tests.utils import load_test_resource


class TestPricelineUnit(TestCase):
    def test_hotel_express_location_search(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        location = "800046992"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search_request = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=occupancy, location_name=location
        )

        priceline_city_search_resource = load_test_resource("priceline/city_search_results.json")
        endpoint = transport.endpoint(PricelineTransport.Endpoint.HOTEL_EXPRESS)
        with requests_mock.Mocker() as mocker:
            mocker.get(endpoint, text=priceline_city_search_resource)
            results = priceline.search_by_location(search_request)

        print(results)
