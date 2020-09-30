from datetime import datetime, timedelta

from api.booking import booking_service
from api.common import cache_storage
from api.common.models import RateType, RoomRate
from api.hotel import hotel_service
from api.hotel.adapters.hotelbeds.hotelbeds import HotelBeds
from api.hotel.hotel_model import (
    HotelLocationSearch,
    RoomOccupancy,
)
from api.models.models import HotelBooking
from api.tests import test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestHotelBedsIntegration(SimplenightTestCase):
    def setUp(self) -> None:
        super().setUp()
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

    def test_hotelbeds_booking(self):
        checkin = datetime.now().date() + timedelta(days=30)
        checkout = datetime.now().date() + timedelta(days=35)
        search = HotelLocationSearch(
            start_date=checkin,
            end_date=checkout,
            occupancy=RoomOccupancy(adults=1),
            location_id="SFO",
            provider="hotelbeds",
        )

        availability_response = hotel_service.search_by_location(search)

        # Find first hotel with a bookable rate
        room_to_book = None
        for hotel in availability_response:
            for room in hotel.room_types:
                if room.rate_type == RateType.BOOKABLE:
                    room_to_book = room
                    break

        self.assertIsNotNone(room_to_book)

        booking_request = test_objects.booking_request(provider="hotelbeds", rate_code=room_to_book.code)
        booking_response = booking_service.book(booking_request)

        provider_rate: RoomRate = cache_storage.get(room_to_book.code)
        assert booking_response.reservation.room_rates[0].code == provider_rate.code

        hotel_booking = HotelBooking.objects.filter(record_locator=booking_response.reservation.locator.id).first()
        assert hotel_booking.provider_total == provider_rate.total.amount
        assert hotel_booking.total_price == room_to_book.total.amount

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
            location_id=location_name,
            start_date=checkin,
            end_date=checkout,
            daily_rates=True,
            occupancy=RoomOccupancy(),
        )

        return search_request
