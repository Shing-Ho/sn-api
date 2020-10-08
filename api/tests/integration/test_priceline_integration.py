from datetime import timedelta, datetime
from unittest.mock import patch

import requests_mock
from freezegun import freeze_time

from api.booking import booking_service
from api.common.models import RoomOccupancy, RateType
from api.hotel import hotel_service
from api.hotel.adapters.priceline.priceline import PricelineAdapter
from api.hotel.adapters.priceline.priceline_info import PricelineInfo
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch, CancellationSummary
from api.models.models import CityMap, Booking, HotelCancellationPolicy
from api.tests import test_objects
from api.tests.integration import test_models
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.tests.utils import load_test_resource


class TestPricelineUnit(SimplenightTestCase):
    def setUp(self) -> None:
        super().setUp()
        provider = test_models.create_provider("priceline")
        provider.save()

        test_models.create_geoname(1, "San Francisco", "CA", "US", population=100)
        test_models.create_provider_city(
            provider.name, code="800046992", name="San Francisco", province="CA", country="US"
        )

        CityMap.objects.create(simplenight_city_id=1, provider=provider, provider_city_id=800046992)

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
        self.assertIsNotNone(results.start_date)
        self.assertIsNotNone(results.end_date)
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

        location = "1"
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        occupancy = RoomOccupancy()
        search_request = HotelLocationSearch(
            start_date=checkin, end_date=checkout, occupancy=occupancy, location_id=location
        )

        resource_file = "priceline/priceline-hotel-express-city-cancellable-rates.json"
        priceline_city_search_resource = load_test_resource(resource_file)

        endpoint = transport.endpoint(PricelineTransport.Endpoint.HOTEL_EXPRESS)
        with requests_mock.Mocker() as mocker:
            mocker.get(endpoint, text=priceline_city_search_resource)
            results = priceline.search_by_location(search_request)

        self.assertEqual(10, len(results))
        self.assertEqual("St. Regis San Francisco", results[0].hotel_details.name)
        self.assertEqual("The Mosser Hotel", results[1].hotel_details.name)
        self.assertEqual(CancellationSummary.NON_REFUNDABLE, results[0].rate_plans[0].cancellation_policy.summary)
        self.assertEqual(CancellationSummary.FREE_CANCELLATION, results[1].rate_plans[0].cancellation_policy.summary)

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
        self.assertEqual("30796806215", booking_response.reservation.locator.id)
        self.assertEqual("CONF0", booking_response.reservation.hotel_locator[0].id)
        self.assertIsNotNone(booking_response.reservation.checkin)
        self.assertIsNotNone(booking_response.reservation.checkout)
        self.assertEqual(1, booking_response.reservation.traveler.occupancy.adults)
        self.assertEqual("John", booking_response.reservation.traveler.first_name)
        self.assertEqual("Simplenight", booking_response.reservation.traveler.last_name)
        self.assertEqual(RateType.BOOKABLE, booking_response.reservation.room_rate.rate_type)

    @freeze_time("2020-10-01")
    def test_priceline_booking_service_cancellation_policies(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin,
            end_date=checkout,
            occupancy=RoomOccupancy(adults=1),
            location_id="1",
            provider="priceline",
        )

        resource_file = "priceline/priceline-hotel-express-city-cancellable-rates.json"
        priceline_city_search_resource = load_test_resource(resource_file)
        priceline_booking_response = load_test_resource("priceline/booking-response-cancellable.json")
        priceline_recheck_response = load_test_resource("priceline/recheck-response.json")

        transport = PricelineTransport(test_mode=True)
        avail_endpoint = transport.endpoint(PricelineTransport.Endpoint.HOTEL_EXPRESS)
        book_endpoint = transport.endpoint(PricelineTransport.Endpoint.EXPRESS_BOOK)
        recheck_endpoint = transport.endpoint(PricelineTransport.Endpoint.EXPRESS_CONTRACT)

        with patch("stripe.Token.create") as stripe_token_mock:
            stripe_token_mock.return_value = {"id": "tok_foo"}

            with patch("stripe.Charge.create") as stripe_create_mock:
                stripe_create_mock.return_value = {
                    "currency": "USD",
                    "id": "payment-id",
                    "amount": 100.00,
                    "object": "settled",
                }

                with requests_mock.Mocker() as mocker:
                    mocker.get(avail_endpoint, text=priceline_city_search_resource)
                    mocker.post(recheck_endpoint, text=priceline_recheck_response)
                    mocker.post(book_endpoint, text=priceline_booking_response)
                    availability_response = hotel_service.search_by_location(search)

                    self.assertTrue(len(availability_response) >= 1)
                    self.assertTrue(len(availability_response[0].room_types) >= 1)

                    hotel_to_book = availability_response[0]
                    room_to_book = hotel_to_book.room_types[0]
                    booking_request = test_objects.booking_request(
                        provider=PricelineInfo.name, rate_code=room_to_book.code
                    )

                    booking_response = booking_service.book(booking_request)
                    print(booking_response)

        booking = Booking.objects.get(transaction_id=booking_response.transaction_id)
        booking_id = booking.booking_id
        cancellation_policies = HotelCancellationPolicy.objects.filter(hotel_booking__booking__booking_id=booking_id)

        self.assertEqual(3, len(cancellation_policies))
        self.assertEqual("FREE_CANCELLATION", cancellation_policies[0].cancellation_type)
        self.assertEqual("2017-02-04", str(cancellation_policies[0].begin_date))
        self.assertEqual("2020-10-29", str(cancellation_policies[0].end_date))

        self.assertEqual("PARTIAL_REFUND", cancellation_policies[1].cancellation_type)
        self.assertEqual("2020-10-29", str(cancellation_policies[1].begin_date))
        self.assertEqual("2020-10-31", str(cancellation_policies[1].end_date))

        self.assertEqual("NON_REFUNDABLE", cancellation_policies[2].cancellation_type)
        self.assertEqual("2020-10-31", str(cancellation_policies[2].begin_date))
        self.assertEqual("2024-07-27", str(cancellation_policies[2].end_date))