from datetime import timedelta, datetime, date

import requests_mock

from api.common.models import RoomOccupancy, RateType
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch
from api.tests import test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.tests.utils import load_test_resource


class TestPricelineUnit(SimplenightTestCase):
    def test_hotel_express_hotel_searcb(self):
        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport)

        hotel_id = "700363264"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search = HotelSpecificSearch(start_date=checkin, end_date=checkout, occupancy=occupancy, hotel_id=hotel_id)

        priceline_hotel_id_response = load_test_resource("priceline/hotel_specific_search_response.json")
        endpoint = transport.endpoint(PricelineTransport.Endpoint.HOTEL_EXPRESS)
        with requests_mock.Mocker() as mocker:
            mocker.get(endpoint, text=priceline_hotel_id_response)
            results = priceline.search_by_id(search)

        self.assertEqual("priceline", results.provider)
        self.assertEqual("700363264", results.hotel_id)
        self.assertEqual(date(2020, 10, 4), results.start_date)
        self.assertEqual(date(2020, 10, 9), results.end_date)
        self.assertEqual(1, results.occupancy.adults)

        self.assertEqual("Best Western Plus Bayside Hotel", results.hotel_details.name)
        self.assertEqual("1717 Embarcadero", results.hotel_details.address.address1)
        self.assertEqual("Oakland", results.hotel_details.address.city)
        self.assertEqual("CA", results.hotel_details.address.province)
        self.assertEqual("US", results.hotel_details.address.country)
        self.assertEqual("CA 94606", results.hotel_details.address.postal_code)
        self.assertIn("This bay front Oakland hotel", results.hotel_details.property_description)

        self.assertAlmostEqual(701.70, float(results.room_rates[0].total_base_rate.amount))
        self.assertEqual("USD", results.room_rates[0].total_base_rate.currency)

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

        self.assertEqual(2, len(results))
        self.assertEqual("Club Wyndham Canterbury", results[0].hotel_details.name)
        self.assertEqual("Best Western Plus Bayside Hotel", results[1].hotel_details.name)

    def test_priceline_booking(self):
        booking_request = test_objects.booking_request()
        priceline_booking_response = load_test_resource("priceline/booking-response.json")

        transport = PricelineTransport(test_mode=True)
        priceline = PricelineAdapter(transport=PricelineTransport(test_mode=True))
        endpoint = transport.endpoint(PricelineTransport.Endpoint.EXPRESS_BOOK)

        with requests_mock.Mocker() as mocker:
            mocker.post(endpoint, text=priceline_booking_response)
            booking_response = priceline.booking(booking_request)

        self.assertEqual(1, booking_response.api_version)
        self.assertIsNotNone(booking_response.transaction_id)
        self.assertTrue(booking_response.status.success)
        self.assertEqual("success", booking_response.status.message)
        self.assertEqual("30796806215", booking_response.reservation.locator)
        self.assertEqual("CONF0", booking_response.reservation.hotel_locator[0])
        self.assertEqual(date(2020, 9, 14), booking_response.reservation.checkin)
        self.assertEqual(date(2020, 9, 16), booking_response.reservation.checkout)
        self.assertEqual(1, booking_response.reservation.traveler.occupancy.adults)
        self.assertEqual("John", booking_response.reservation.traveler.first_name)
        self.assertEqual("Simplenight", booking_response.reservation.traveler.last_name)
        self.assertEqual(RateType.BOOKABLE, booking_response.reservation.room_rates[0].rate_type)
