import unittest
import uuid
from datetime import datetime, timedelta

from api.booking.booking_model import HotelBookingRequest, Customer, Traveler
from api.common.models import RateType, RoomRate, Money
from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.hotel_model import (
    HotelLocationSearch,
    RoomOccupancy,
)


class TestHotelBedsIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.hotelbeds = HotelBeds()

    def test_location_search(self):
        search_request = self.create_location_search()
        response = self.hotelbeds.search_by_location(search_request)
        print(response)

    def test_location_search_bad_location(self):
        search_request = self.create_location_search(location_name="XXX")
        response = self.hotelbeds.search_by_location(search_request)
        assert len(response) == 0

    def test_hotel_details(self):
        hotel_codes = ["123456", "654321"]
        response = self.hotelbeds.details(hotel_codes, "en_US")
        print(response)

    def test_hotel_booking(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search_request = self.create_location_search(checkin=checkin, checkout=checkout)

        response = self.hotelbeds.search_by_location(search_request)

        rate_key = response[10].room_types[1].rates[1].rate_key

        transaction_id = str(uuid.uuid4())[:8]
        booking_request = HotelBookingRequest(
            api_version=1,
            transaction_id=transaction_id,
            hotel_id="123",
            checkin=checkin,
            checkout=checkout,
            language=search_request.language,
            customer=Customer("John", "Smith", "5558675309", "john@smith.foo", "US"),
            traveler=Traveler("John", "Smith", occupancy=search_request.occupancy),
            room_rate=RoomRate(
                rate_key=rate_key,
                rate_type=RateType.BOOKABLE,
                description="",
                total_base_rate=Money(0.0, "USD"),
                total_tax_rate=Money(0.0, "USD"),
                total=Money(0.0, "USD"),
                additional_detail=[],
            ),
            payment=None,
        )

        booking_response = self.hotelbeds.booking(booking_request)
        print(booking_response)

    def test_recheck_hotel(self):
        search_request = self.create_location_search()

        hotels = self.hotelbeds.search_by_location(search_request)
        assert len(hotels) > 0

        response = self.hotelbeds.recheck(search_request, hotels[0].room_types[0].rates[0].rate_key)
        print(response)

    @staticmethod
    def create_location_search(location_name="TVL", checkin=None, checkout=None):
        if checkin is None:
            checkin = datetime.now().date() + timedelta(days=30)

        if checkout is None:
            checkout = datetime.now().date() + timedelta(days=35)

        search_request = HotelLocationSearch(
            location_name=location_name,
            start_date=checkin,
            end_date=checkout,
            daily_rates=True,
            occupancy=RoomOccupancy(),
        )

        return search_request
