from datetime import datetime, timedelta

from api.common.models import RoomOccupancy
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch
from api.tests import test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestPricelineIntegration(SimplenightTestCase):
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
        search = HotelSpecificSearch(start_date=checkin, end_date=checkout, occupancy=occupancy, hotel_id=hotel_id)

        results = priceline.search_by_id(search)
        print(results)

    def test_recheck_room_rate(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        hotel_id = "700363264"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search = HotelSpecificSearch(start_date=checkin, end_date=checkout, occupancy=occupancy, hotel_id=hotel_id)

        results = priceline.search_by_id(search)
        self.assertTrue(len(results.room_rates) >= 1)

        verified_rate = priceline.recheck(results.room_rates[0])
        print(verified_rate)

    def test_booking(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=occupancy, location_name="800046992"
        )

        availability_response = priceline.search_by_location(search)
        hotel = availability_response[0]

        payment_object = test_objects.payment("4111111111111111")

        room_rate_to_book = priceline.room_details(hotel.room_rates[0].code)

        booking_request = test_objects.booking_request(payment_object, rate=room_rate_to_book)

        booking_request.customer.first_name = "James"
        booking_request.customer.last_name = "Morton"
        booking_request.customer.email = "jmorton@simplenight.com"

        booking_response = priceline.booking(booking_request)

        print(booking_response)
        self.assertIsNotNone(booking_response.reservation.locator)
