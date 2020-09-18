import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
import requests_mock

from api.common.models import RoomOccupancy
from api.hotel import core_hotel_service, hotel_service, converter, hotel_cache_service
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.converter.google_models import RoomParty, GoogleHotelSearchRequest
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch
from api.tests import test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.tests.utils import load_test_resource
from api.view.exceptions import AvailabilityException


class TestCoreHotelService(SimplenightTestCase):
    def test_markups_applied_and_stored_in_cache(self):
        search_request = HotelLocationSearch(
            location_id="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            provider="stub",
        )

        hotels = core_hotel_service.search_by_location(search_request)
        room_rates = [room_rate for hotel in hotels for room_rate in hotel.room_rates]
        assert len(room_rates) > 10

        for room_rate in room_rates:
            stored_provider_rate_payload = hotel_cache_service.get_provider_rate(room_rate.code)
            provider_rate = stored_provider_rate_payload.provider_rate

            assert provider_rate is not None
            assert provider_rate.total.amount < room_rate.total.amount

    def test_error_in_api_response(self):
        error_response = load_test_resource("hotelbeds/error-response.json")
        with requests_mock.Mocker() as mocker:
            mocker.post(HotelBedsTransport.get_hotels_url(), text=error_response)
            search_request = HotelLocationSearch(
                location_id="SFO",
                start_date=date(2020, 1, 20),
                end_date=date(2020, 1, 27),
                occupancy=RoomOccupancy(2, 1),
                provider="hotelbeds",
            )

            with pytest.raises(AvailabilityException) as e:
                hotel_service.search_by_location(search_request)

            assert "The check-in must be in the future" in e.value.detail

    def test_calculate_min_nightly_rate(self):
        rate_one = test_objects.room_rate(rate_key="one", total="200", tax_rate="40", base_rate="160")
        rate_two = test_objects.room_rate(rate_key="two", total="500", tax_rate="350", base_rate="85")
        rate_three = test_objects.room_rate(rate_key="three", total="100", tax_rate="15", base_rate="85")
        rate_four = test_objects.room_rate(rate_key="four", total="120", tax_rate="25", base_rate="95")

        room_type_one = test_objects.room_type()
        room_type_two = test_objects.room_type()

        hotel = test_objects.hotel(room_rates=[rate_one, rate_two, rate_three, rate_four])
        hotel.start_date = date(2020, 1, 1)
        hotel.end_date = date(2020, 1, 2)
        hotel.room_types = [room_type_one, room_type_two]

        # Room Nights = 1
        min_nightly_base, min_nightly_tax, min_nightly_total = core_hotel_service._calculate_hotel_min_nightly_rates(hotel)
        assert min_nightly_base == 85
        assert min_nightly_tax == 15
        assert min_nightly_total == 100

        # Room Nights = 2
        hotel.end_date = date(2020, 1, 3)
        min_nightly_base, min_nightly_tax, min_nightly_total = core_hotel_service._calculate_hotel_min_nightly_rates(hotel)
        assert min_nightly_base == 42.5
        assert min_nightly_tax == 7.50
        assert min_nightly_total == 50

        # Same Date, Room Nights = 1
        hotel.end_date = date(2020, 1, 1)
        min_nightly_base, min_nightly_tax, min_nightly_total = core_hotel_service._calculate_hotel_min_nightly_rates(hotel)
        assert min_nightly_base == 85
        assert min_nightly_tax == 15
        assert min_nightly_total == 100

    def test_search_by_hotel_id_google(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
            provider="stub",
        )

        google_search_request = GoogleHotelSearchRequest(
            api_version=1,
            transaction_id=str(uuid.uuid4()),
            hotel_id=search_request.hotel_id,
            start_date=search_request.start_date,
            end_date=search_request.end_date,
            party=RoomParty(adults=search_request.occupancy.adults, children=[]),
        )

        hotel = core_hotel_service.search_by_id(search_request)
        google_hotel = converter.google.convert_hotel_response(google_search_request, hotel)

        self.assertIsNotNone(google_hotel)

    def test_min_nightly_rates_included_in_response(self):
        search_request = HotelLocationSearch(
            location_id="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 22),
            occupancy=RoomOccupancy(2, 1),
            provider="stub",
        )

        room_rate = test_objects.room_rate(rate_key="foo", total="100", base_rate="80", tax_rate="20")
        room_type = test_objects.room_type()

        hotel = test_objects.hotel(room_rates=[room_rate])
        hotel.start_date = date(2020, 1, 1)
        hotel.end_date = date(2020, 1, 3)  # Two room nights
        hotel.room_types = [room_type]

        stub_adapter = StubHotelAdapter()
        stub_adapter.search_by_location = lambda x: [hotel]

        with patch("api.hotel.adapters.adapter_service.get_adapters") as mock_adapter_service:
            mock_adapter_service.return_value = [stub_adapter]
            hotels = core_hotel_service.search_by_location(search_request)

        # Two Room Nights, So average nightly rate is 0.5 Total
        # Average is applied after default markup of 18%
        self.assertEqual(Decimal("59.00"), hotels[0].average_nightly_rate)
        self.assertEqual(Decimal("47.20"), hotels[0].average_nightly_base)
        self.assertEqual(Decimal("11.80"), hotels[0].average_nightly_tax)