from datetime import datetime, timedelta

from api.booking import booking_service
from api.common.models import RoomOccupancy
from api.hotel import hotel_service
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_info import PricelineInfo
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch
from api.models.models import CityMap
from api.tests import test_objects
from api.tests.integration import test_models
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestPricelineIntegration(SimplenightTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.provider = test_models.create_provider("priceline")
        self.provider.save()

        test_models.create_geoname(1, "San Francisco", "CA", "US", population=100)
        test_models.create_provider_city(
            self.provider.name, code="800046992", name="San Francisco", province="CA", country="US"
        )

        CityMap.objects.create(simplenight_city_id=1, provider=self.provider, provider_city_id=800046992)

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

        location = "1"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search_request = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=occupancy, location_id=location
        )

        results = priceline.search_by_location(search_request)
        self.assertIsNotNone(results)
        self.assertTrue(len(results) > 1)

    def test_hotel_express_hotel_availability(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        hotel_id = "700363264"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search = HotelSpecificSearch(start_date=checkin, end_date=checkout, occupancy=occupancy, hotel_id=hotel_id)

        results = priceline.search_by_id(search)
        self.assertIsNotNone(results)
        self.assertEqual("700363264", results.hotel_id)
        self.assertEqual("Best Western Plus Bayside Hotel", results.hotel_details.name)

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
        self.assertIsNotNone(verified_rate)
        self.assertIsNotNone(verified_rate.code)

    def test_booking(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=occupancy, location_id="1"
        )

        availability_response = priceline.search_by_location(search)
        hotel = availability_response[0]

        payment_object = test_objects.payment("4111111111111111")

        room_rate_to_book = priceline.room_details(hotel.room_rates[0].code)

        booking_request = test_objects.booking_request(payment_object, rate_code=room_rate_to_book.code)

        booking_request.customer.first_name = "James"
        booking_request.customer.last_name = "Morton"
        booking_request.customer.email = "jmorton@simplenight.com"

        booking_response = priceline.booking(booking_request)

        print(booking_response)
        self.assertIsNotNone(booking_response.reservation.locator)

    def test_priceline_booking_service(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin,
            end_date=checkout,
            occupancy=RoomOccupancy(adults=1),
            location_id="1",
            provider="priceline",
        )

        availability_response = hotel_service.search_by_location(search)
        self.assertTrue(len(availability_response) >= 1)
        self.assertTrue(len(availability_response[0].room_types) >= 1)

        hotel_to_book = availability_response[0]
        room_to_book = hotel_to_book.room_types[0]
        booking_request = test_objects.booking_request(provider=PricelineInfo.name, rate_code=room_to_book.code)
        booking_response = booking_service.book(booking_request)

        print(booking_response)