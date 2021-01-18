from datetime import date
from unittest.mock import patch

import requests_mock

from api.common.common_models import from_json
from api.hotel.adapters.hotelbeds.hotelbeds_adapter import HotelbedsAdapter
from api.hotel.adapters.hotelbeds.hotelbeds_transport import HotelbedsTransport
from api.hotel.models.hotel_api_model import HotelLocationSearch, SimplenightHotel
from api.hotel.models.hotel_common_models import RoomOccupancy
from api.tests.unit.simplenight_test_case import SimplenightTestCase
from api.tests.utils import load_test_resource
from api.tests import model_helper

BOOKING_ENDPOINT = "/api/v1/hotels/booking"
SEARCH_BY_LOCATION = "/api/v1/hotels/search-by-location"


class TestBookingView(SimplenightTestCase):
    def test_hotelbeds_availability(self):
        hotelbeds_location_response = load_test_resource("hotelbeds/search-by-location-response.json")
        hotelbeds_content_response = load_test_resource("hotelbeds/hotel-details-response.json")
        model_helper.create_provider(HotelbedsAdapter.get_provider_name())

        search_request = HotelLocationSearch(
            location_id="SFO",
            start_date=date(2020, 1, 20),
            end_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(adults=2, children=1),
            provider="hotelbeds",
        )

        with patch("api.hotel.hotel_mappings.find_simplenight_hotel_id") as mock_find_simplenight_id:
            mock_find_simplenight_id.return_value = "123"
            transport = HotelbedsTransport()
            hotels_url = transport.endpoint(transport.Endpoint.HOTELS)
            content_url = transport.endpoint(transport.Endpoint.HOTEL_CONTENT)

            with patch("api.locations.location_service.find_provider_location") as mock_location_service:
                mock_location_service.return_value = model_helper.create_provider_city(
                    provider_name=HotelbedsAdapter.get_provider_name(),
                    code="SFO",
                    name="San Francisco",
                    province="CA",
                    country="US",
                )

                with requests_mock.Mocker() as mocker:
                    mocker.post(hotels_url, text=hotelbeds_location_response)
                    mocker.get(content_url, text=hotelbeds_content_response)
                    response = self.post(SEARCH_BY_LOCATION, search_request)

                hotels = from_json(response.content, SimplenightHotel, many=True)
                assert len(hotels) == 24
