import unittest
from datetime import date

import requests_mock

from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.adapters.hotelbeds.search import HotelBedsSearchBuilder, HotelBedsPaymentType, HotelBedsRateType
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.hotels import HotelLocationSearch, to_json, RoomOccupancy
from api.tests.utils import load_test_resource


class TestHotelBeds(unittest.TestCase):
    def test_default_headers_in_transport(self):
        transport = HotelBedsTransport()
        default_headers = transport.get_headers()
        self.assertIn("Api-Key", default_headers)
        self.assertIn("X-Signature", default_headers)
        self.assertEqual("gzip", default_headers["Accept-Encoding"])
        self.assertEqual("application/json", default_headers["Content-Type"])

        headers = transport.get_headers(foo="bar")
        self.assertIn("Api-Key", headers)
        self.assertEqual("bar", headers["foo"])

    def test_headers_return_copy(self):
        transport = HotelBedsTransport()
        transport.get_headers()["foo"] = "bar"
        self.assertNotIn("foo", transport.get_headers())

    def test_build_search_request(self):
        search_builder = HotelBedsSearchBuilder()
        location_search = HotelLocationSearch(
            location_name="SFO",
            checkin_date=date(2020, 1, 1),
            checkout_date=date(2020, 1, 7),
            occupancy=RoomOccupancy(adults=2, children=1),
        )

        hotelbeds_request = search_builder.build(location_search)
        self.assertEqual("SFO", hotelbeds_request.destination.code)
        self.assertEqual("2020-01-01", str(hotelbeds_request.stay.checkin))
        self.assertEqual("2020-01-07", str(hotelbeds_request.stay.checkout))
        self.assertEqual(2, hotelbeds_request.occupancies[0].adults)
        self.assertEqual(1, hotelbeds_request.occupancies[0].children)

        hotelbeds_request_json = to_json(hotelbeds_request)
        self.assertEqual("SFO", hotelbeds_request_json["destination"]["code"])
        self.assertEqual("2020-01-01", hotelbeds_request_json["stay"]["checkIn"])
        self.assertEqual("2020-01-07", hotelbeds_request_json["stay"]["checkOut"])
        self.assertEqual(2, hotelbeds_request_json["occupancies"][0]["adults"])
        self.assertEqual(1, hotelbeds_request_json["occupancies"][0]["children"])

    def test_hotelbeds_search_by_location_parsing(self):
        resource = load_test_resource("hotelbeds/search-by-location-response.json")
        hotelbeds = HotelBeds()

        search = HotelLocationSearch(
            location_name="FOO",
            checkin_date=date(2020, 1, 1),
            checkout_date=date(2020, 1, 7),
            occupancy=RoomOccupancy(adults=1),
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

        self.assertEqual("100.17", hotel.min_rate)
        self.assertEqual("1001.66", hotel.max_rate)
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
        self.assertEqual("100.17", rate.net)
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
