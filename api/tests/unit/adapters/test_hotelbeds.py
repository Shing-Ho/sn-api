import json
from datetime import date, datetime, timedelta
from decimal import Decimal

import requests_mock
from django.test import TestCase

from api.hotel.models.booking_model import HotelBookingRequest, Customer, Traveler
from api.common.models import to_json, RoomOccupancy
from api.hotel.adapters.hotelbeds.hotelbeds_common_models import HotelBedsRateType, HotelBedsPaymentType
from api.hotel.adapters.hotelbeds.hotelbeds_adapter import HotelBeds
from api.hotel.adapters.hotelbeds.hotelbeds_search_models import HotelBedsSearchBuilder
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.models.hotel_api_model import SimplenightAmenities
from api.hotel.models.adapter_models import AdapterLocationSearch, AdapterOccupancy
from api.tests import test_objects
from api.tests.utils import load_test_resource, load_test_json_resource


class TestHotelBeds(TestCase):
    def test_default_headers_in_transport(self):
        transport = HotelBedsTransport()
        default_headers = transport._get_headers()
        self.assertIn("Api-Key", default_headers)
        self.assertIn("X-Signature", default_headers)
        self.assertEqual("gzip", default_headers["Accept-Encoding"])
        self.assertEqual("application/json", default_headers["Content-Type"])

        headers = transport._get_headers(foo="bar")
        self.assertIn("Api-Key", headers)
        self.assertEqual("bar", headers["foo"])

    def test_headers_return_copy(self):
        transport = HotelBedsTransport()
        transport._get_headers()["foo"] = "bar"
        self.assertNotIn("foo", transport._get_headers())

    def test_build_search_request(self):
        search_builder = HotelBedsSearchBuilder()
        location_search = AdapterLocationSearch(
            location_id="SFO",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 1, 7),
            occupancy=AdapterOccupancy(adults=2, children=1),
        )

        hotelbeds_request = search_builder.build(location_search)
        self.assertEqual("SFO", hotelbeds_request.destination.code)
        self.assertEqual("2020-01-01", str(hotelbeds_request.stay.checkIn))
        self.assertEqual("2020-01-07", str(hotelbeds_request.stay.checkOut))
        self.assertEqual(2, hotelbeds_request.occupancies[0].adults)
        self.assertEqual(1, hotelbeds_request.occupancies[0].children)

        hotelbeds_request_json = json.loads(to_json(hotelbeds_request))
        self.assertEqual("SFO", hotelbeds_request_json["destination"]["code"])
        self.assertEqual("2020-01-01", hotelbeds_request_json["stay"]["checkIn"])
        self.assertEqual("2020-01-07", hotelbeds_request_json["stay"]["checkOut"])
        self.assertEqual(2, hotelbeds_request_json["occupancies"][0]["adults"])
        self.assertEqual(1, hotelbeds_request_json["occupancies"][0]["children"])

    def test_hotelbeds_search_by_location_parsing(self):
        resource = load_test_resource("hotelbeds/search-by-location-response.json")
        hotelbeds = HotelBeds()

        search = AdapterLocationSearch(
            location_id="FOO",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 1, 7),
            occupancy=AdapterOccupancy(adults=1),
        )

        with requests_mock.Mocker() as mocker:
            mocker.post(HotelBedsTransport.get_hotels_url(), text=resource)
            results = hotelbeds._search_by_location(search)

        self.assertEqual("296", results.audit_data.process_time)
        self.assertEqual("2020-06-28 21:01:35.496000", str(results.audit_data.timestamp))
        expected_host = "ip-10-185-89-125.eu-west-1.compute.internal.node.int-hbg-aws-eu-west-1.discovery"
        self.assertEqual(expected_host, results.audit_data.server_id)

        self.assertEqual(24, results.results.total)
        self.assertEqual(24, len(results.results.hotels))
        self.assertEqual("2020-07-28", str(results.results.checkin))
        self.assertEqual("2020-08-02", str(results.results.checkout))

        hotel = results.results.hotels[0]
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
        self.assertEqual(HotelBedsRateType.RECHECK, rate.rate_type)
        self.assertEqual(HotelBedsPaymentType.AT_WEB, rate.payment_type)
        self.assertFalse(rate.packaging)
        self.assertEqual(1, rate.rooms)
        self.assertEqual(0, rate.children)
        self.assertEqual(0, len(rate.promotions))
        self.assertEqual(1, len(rate.taxes.taxes))
        self.assertEqual(2, len(rate.cancellation_policies))

        self.assertEqual("2020-07-20 23:59:00-07:00", str(rate.cancellation_policies[0].deadline))
        self.assertEqual("50.08", rate.cancellation_policies[0].amount)

    def test_hotelbeds_hotel_details(self):
        hotel_details_resource = load_test_resource("hotelbeds/hotel-details-response.json")
        hotelbeds = HotelBeds()
        with requests_mock.Mocker() as mocker:
            mocker.get(HotelBedsTransport.get_hotel_content_url(), text=hotel_details_resource)
            response = hotelbeds.details(["foo", "bar"], "en_US")

        self.assertIsNotNone(response)

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

        hotelbeds = HotelBeds()
        booking_resource = load_test_resource("hotelbeds/booking-confirmation-response.json")
        with requests_mock.Mocker() as mocker:
            mocker.post(HotelBedsTransport.get_booking_url(), text=booking_resource)
            booking_response = hotelbeds.booking(booking_request)

        self.assertIsNotNone(booking_response)

    def test_search_location_with_bad_location(self):
        response = {
            "auditData": {
                "processTime": "2",
                "timestamp": "2020-07-20 09:47:39.281",
                "requestHost": "66.201.49.52, 70.132.18.144, 10.185.80.230, 10.185.88.177",
                "serverId": "ip-10-185-88-234.eu-west-1.compute.internal.node.int-hbg-aws-eu-west-1.discovery",
                "environment": "[awseuwest1, awseuwest1a, ip_10_185_88_234]",
                "release": "cf7383046266bc1f203fb637fed444271a3717e7",
                "token": "5E0FD19A79034FD19D89A8948A5AA697",
                "internal": "0||UK|01|0|0||||||||||||0||1~1~1~0|0|0||0|ba99fa9f7b504eae563b35b294ef2dcc||||",
            },
            "hotels": {"total": 0},
        }

        hotelbeds_service = HotelBeds(HotelBedsTransport())
        request = self.create_location_search("foo")
        with requests_mock.Mocker() as mocker:
            mocker.post(HotelBedsTransport.get_hotels_url(), json=response)
            mocker.get(HotelBedsTransport.get_hotel_content_url())
            results = hotelbeds_service.search_by_location(request)

        assert len(results) == 0

    def test_hotelbeds_amenity_mappings(self):
        resource = load_test_json_resource("hotelbeds/hotel-details-single-hotel.json")
        with requests_mock.Mocker() as mocker:
            mocker.get(HotelBedsTransport.get_hotel_content_url(), json=resource)
            hotelbeds = HotelBeds(HotelBedsTransport())
            details = hotelbeds.details([], "ENG")

        self.assertEqual(1, len(details))

        hotel_detail = details[0]
        self.assertEquals(10, len(hotel_detail.amenities))
        self.assertIn(SimplenightAmenities.RESTAURANT, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.POOL, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.PARKING, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.BAR, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.GYM, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.BREAKFAST, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.AIR_CONDITIONING, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.PET_FRIENDLY, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.RESTAURANT, hotel_detail.amenities)
        self.assertIn(SimplenightAmenities.WASHER_DRYER, hotel_detail.amenities)

    def test_hotelbeds_recheck(self):
        search_request = self.create_location_search(location_id="SFO")

        avail_response = load_test_resource("hotelbeds/recheck/availability.json")
        details_response = load_test_resource("hotelbeds/recheck/details.json")
        recheck_response = load_test_resource("hotelbeds/recheck/recheck.json")

        hotel_details_url = "https://api.test.hotelbeds.com/hotel-content-api/1.0/hotels?language=ENG"

        hotelbeds = HotelBeds(HotelBedsTransport())
        with requests_mock.Mocker() as mocker:
            mocker.post(HotelBedsTransport.get_hotels_url(), text=avail_response)
            mocker.get(hotel_details_url, text=details_response)
            mocker.post(HotelBedsTransport.get_checkrates_url(), text=recheck_response)

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
