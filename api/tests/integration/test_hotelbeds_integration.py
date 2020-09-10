import uuid
from datetime import datetime, timedelta

from django.test import TestCase

from api.booking.booking_model import HotelBookingRequest, Customer, Traveler
from api.common.models import RateType, RoomRate
from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.hotel_model import (
    HotelLocationSearch,
    RoomOccupancy,
)
from api.tests import to_money


class TestHotelBedsIntegration(TestCase):
    def setUp(self) -> None:
        self.hotelbeds = HotelBeds()

    def test_location_search(self):
        search_request = self.create_location_search()
        self.hotelbeds.search_by_location(search_request)

    def test_location_recheck(self):
        search_request = self.create_location_search()
        response = self.hotelbeds.search_by_location(search_request)

        self.assertTrue(len(response) >= 1)

        room_rate_to_check = response[0].room_rates[0]
        room_rate_verified = self.hotelbeds.recheck(room_rate_to_check)

        print(room_rate_to_check)
        print(room_rate_verified)

    def test_location_search_bad_location(self):
        search_request = self.create_location_search(location_name="XXX")
        response = self.hotelbeds.search_by_location(search_request)
        assert len(response) == 0

    def test_hotel_details(self):
        hotel_codes = ["123456", "654321"]
        self.hotelbeds.details(hotel_codes, "en_US")

    def test_hotel_booking(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search_request = self.create_location_search(checkin=checkin, checkout=checkout)

        response = self.hotelbeds.search_by_location(search_request)

        room_rate_to_book = response[0].room_rates[0]

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
            room_rates=[
                RoomRate(
                    code=room_rate_to_book.code,
                    rate_plan_code=room_rate_to_book.rate_plan_code,
                    room_type_code=room_rate_to_book.room_type_code,
                    rate_type=RateType.BOOKABLE,
                    total_base_rate=to_money("0.0"),
                    total_tax_rate=to_money("0.0"),
                    total=to_money("0.0"),
                    maximum_allowed_occupancy=room_rate_to_book.maximum_allowed_occupancy,
                )
            ],
            payment=None,
        )

        booking_response = self.hotelbeds.booking(booking_request)
        self.assertIsNotNone(booking_response)

    def test_hotelbeds_facilities_types(self):
        response = self.hotelbeds.get_facilities_types()
        self.assertTrue(len(response) > 0)

    def test_hotelbeds_cateogies(self):
        response = self.hotelbeds.get_categories()
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
