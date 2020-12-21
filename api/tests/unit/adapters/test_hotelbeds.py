from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

import requests_mock

from api.hotel.adapters.hotelbeds.hotelbeds_adapter import HotelbedsAdapter
from api.hotel.adapters.hotelbeds.hotelbeds_common_models import HotelbedsRateType, HotelbedsPaymentType
from api.hotel.adapters.hotelbeds.hotelbeds_transport import HotelbedsTransport
from api.hotel.models.adapter_models import AdapterLocationSearch, AdapterOccupancy
from api.hotel.models.booking_model import HotelBookingRequest, Customer, Traveler
from api.hotel.models.hotel_common_models import RoomOccupancy
from api.tests import test_objects, model_helper
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.tests.utils import load_test_resource


class TestHotelBeds(SimplenightTestCase):
    def test_default_headers_in_transport(self):
        transport = HotelbedsTransport()
        default_headers = transport._get_headers()
        self.assertIn("Api-Key", default_headers)
        self.assertIn("X-Signature", default_headers)
        self.assertEqual("gzip", default_headers["Accept-Encoding"])
        self.assertEqual("application/json", default_headers["Content-Type"])

        headers = transport._get_headers(foo="bar")
        self.assertIn("Api-Key", headers)
        self.assertEqual("bar", headers["foo"])

    def test_headers_return_copy(self):
        transport = HotelbedsTransport()
        transport._get_headers()["foo"] = "bar"
        self.assertNotIn("foo", transport._get_headers())

    def test_hotelbeds_search_by_location_parsing(self):
        resource = load_test_resource("hotelbeds/search-by-location-response.json")
        hotelbeds = HotelbedsAdapter()

        search = AdapterLocationSearch(
            location_id="FOO",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 1, 7),
            occupancy=AdapterOccupancy(adults=1),
        )

        transport = HotelbedsTransport()
        hotels_url = transport.endpoint(transport.Endpoint.HOTELS)

        with requests_mock.Mocker() as mocker:
            mocker.post(hotels_url, text=resource)
            results = hotelbeds.search_by_location(search)

        hotel = results[0]
        self.assertEqual(349168, hotel.code)
        self.assertEqual("Grand Residences - Lake Tahoe", hotel.name)
        self.assertEqual("3EST", hotel.category_code)
        self.assertEqual("3 STARS", hotel.category_name)
        self.assertEqual("TVL", hotel.destination_code)
        self.assertEqual("Lake Tahoe - CA/NV", hotel.destination_name)
        self.assertEqual(1, hotel.zone_code)
        self.assertEqual("South Lake Tahoe", hotel.zone_name)
        self.assertEqual("38.955487637106742", hotel.latitude)
        self.assertEqual("-119.94413940701634", hotel.longitude)
        self.assertEqual(9, len(hotel.rooms))

        self.assertEqual("100.17", str(hotel.min_rate))
        self.assertEqual("1001.66", str(hotel.max_rate))
        self.assertEqual("EUR", hotel.currency)

        room = hotel.rooms[0]
        self.assertEqual("DBL.QN", room.code)
        self.assertEqual("DOUBLE QUEEN SIZE BED", room.name)
        self.assertEqual(4, len(room.rates))

        rate = room.rates[0]
        expected_rate_key = (
            "20200728|20200802|W|256|349168|DBL.QN|ID_B2B_19|RO|RATE1|1~1~0||N@03~~21164~299946933~N"
            "~AC7BF302F70841C159337089520200AAUK0000024002300060121164"
        )
        self.assertEqual(expected_rate_key, rate.rate_key)
        self.assertEqual(9, rate.allotment)
        self.assertEqual("NOR", rate.rate_class)
        self.assertEqual("100.17", str(rate.net))
        self.assertEqual(HotelbedsRateType.RECHECK, rate.rate_type)
        self.assertEqual(HotelbedsPaymentType.AT_WEB, rate.payment_type)
        self.assertFalse(rate.packaging)
        self.assertEqual(1, rate.rooms)
        self.assertEqual(0, rate.children)
        self.assertEqual(0, len(rate.promotions))
        self.assertEqual(1, len(rate.taxes.taxes))
        self.assertEqual(2, len(rate.cancellation_policies))

        self.assertEqual("2020-07-20 23:59:00-07:00", str(rate.cancellation_policies[0].deadline))
        self.assertEqual("50.08", rate.cancellation_policies[0].amount)

    def test_hotelbeds_booking(self):
        room_rate = test_objects.room_rate(rate_key="rate-key", total="0")

        booking_request = HotelBookingRequest(
            api_version=1,
            transaction_id="tx",
            hotel_id="123",
            language="en",
            customer=Customer(
                first_name="John", last_name="Smith", phone_number="5558675309", email="john@smith.foo", country="US"
            ),
            traveler=Traveler(first_name="John", last_name="Smith", occupancy=RoomOccupancy(adults=1)),
            room_code=room_rate.code,
            payment=None,
        )

        transport = HotelbedsTransport()
        hotelbeds = HotelbedsAdapter(transport)
        booking_resource = load_test_resource("hotelbeds/booking-confirmation-response.json")
        booking_url = transport.endpoint(transport.Endpoint.BOOKING)
        with requests_mock.Mocker() as mocker:
            mocker.post(booking_url, text=booking_resource)
            booking_response = hotelbeds.booking(booking_request)

        self.assertIsNotNone(booking_response)

    def test_hotelbeds_recheck(self):
        search_request = self.create_location_search(location_id="SFO")

        avail_response = load_test_resource("hotelbeds/recheck/availability.json")
        details_response = load_test_resource("hotelbeds/recheck/details.json")
        recheck_response = load_test_resource("hotelbeds/recheck/recheck.json")

        hotel_details_url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels?language=ENG"

        transport = HotelbedsTransport()
        hotelbeds = HotelbedsAdapter(transport)
        hotels_url = transport.endpoint(transport.Endpoint.HOTELS)
        checkrates_url = transport.endpoint(transport.Endpoint.CHECKRATES)

        with patch("api.locations.location_service.find_provider_location") as mock_location_service:
            mock_location_service.return_value = model_helper.create_provider_city(
                provider_name=HotelbedsAdapter.get_provider_name(),
                code="SFO",
                name="San Francisco",
                province="CA",
                country="CA",
            )

            with requests_mock.Mocker() as mocker:
                mocker.post(hotels_url, text=avail_response)
                mocker.get(hotel_details_url, text=details_response)
                mocker.post(checkrates_url, text=recheck_response)

                hotels = hotelbeds.search_by_location(search_request)
                assert len(hotels) > 0

                availability_room_rates = hotels[0].room_rates[0]
                recheck_response = hotelbeds.recheck(availability_room_rates)

                self.assertEqual(Decimal("99.89"), availability_room_rates.total.amount)
                self.assertEqual(Decimal("149.84"), recheck_response.total.amount)

    @staticmethod
    def create_location_search(location_id="TVL"):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search_request = AdapterLocationSearch(
            location_id=location_id, start_date=checkin, end_date=checkout, occupancy=AdapterOccupancy(),
        )

        return search_request
