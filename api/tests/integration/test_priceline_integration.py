from datetime import datetime, timedelta

from django.test import TestCase

from api.common.models import RoomOccupancy
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch


class TestPricelineIntegration(TestCase):
    def test_transport_test_mode(self):
        transport = PricelineTransport(test_mode=True)
        hotel_express_url = transport.endpoint(transport.Endpoint.HOTEL_EXPRESS)
        self.assertEqual("https://api-sandbox.rezserver.com/api/hotel/getExpress.Results", hotel_express_url)

        transport = PricelineTransport(test_mode=False)
        hotel_express_url = transport.endpoint(transport.Endpoint.HOTEL_EXPRESS)
        self.assertEqual("https://api.rezserver.com/api/hotel/getExpress.Results", hotel_express_url)

    def test_hotel_express_city_availability(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        location = "800046992"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search_request = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=occupancy, location_name=location
        )

        results = priceline.search_by_location(search_request)
        print(results)

    def test_hotel_express_hotel_availability(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        hotel_id = "700363264"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search = HotelSpecificSearch(
            start_date=checkin, end_date=checkout, occupancy=occupancy, hotel_id=hotel_id
        )

        results = priceline.search_by_id(search)
        print(results)
