import decimal
import random
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Type, Union

from api.booking.booking_model import Reservation, HotelBookingRequest, HotelBookingResponse, Locator, Status
from api.common.models import RateType, RoomRate, DailyRate, Money
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import (
    HotelLocationSearch,
    Hotel,
    RoomOccupancy,
    RoomType,
    Amenity,
    Image,
    ImageType,
    BedTypes,
    CancellationPolicy,
    HotelDetails,
    Address,
    GeoLocation,
    RatePlan,
    BaseHotelSearch,
)
from api.tests.utils import random_alphanumeric
from common.utils import random_string


class StubHotelAdapter(HotelAdapter):
    CRS_NAME = "stub"

    def search_by_location(self, search_request: HotelLocationSearch) -> List[Hotel]:
        num_hotels_to_return = random.randint(10, 50)
        return [self.search_by_id(search_request) for _ in range(num_hotels_to_return)]

    def search_by_id(self, search_request: BaseHotelSearch) -> Hotel:
        hotel_code = random_string(5).upper()
        room_types = self._generate_room_types(search_request)
        response = Hotel(
            crs=self.CRS_NAME,
            hotel_id=hotel_code,
            start_date=search_request.start_date,
            end_date=search_request.end_date,
            occupancy=RoomOccupancy(2, 2),
            room_types=room_types,
            hotel_details=self._generate_hotel_details(),
        )

        return response

    def recheck(self, room_rates: Union[RoomRate, List[RoomRate]]) -> List[RoomRate]:
        pass

    def details(self, *args):
        pass

    def booking_availability(self, search_request: BaseHotelSearch):
        return self.search_by_id(search_request)

    def booking(self, book_request: HotelBookingRequest) -> HotelBookingResponse:
        reservation = Reservation(
            locator=Locator(str(uuid.uuid4())),
            hotel_locator=Locator(random_alphanumeric(6)),
            hotel_id=book_request.hotel_id,
            checkin=book_request.checkin,
            checkout=book_request.checkout,
            customer=book_request.customer,
            traveler=book_request.traveler,
            room_rates=book_request.room_rates,
        )

        return HotelBookingResponse(
            api_version=1, transaction_id=str(uuid.uuid4()), status=Status(True, "Success"), reservation=reservation
        )

    def _generate_room_types(self, search_request: BaseHotelSearch):
        bed_types = {
            "King": BedTypes(king=1),
            "Queen": BedTypes(queen=random.randint(1, 2)),
            "Double": BedTypes(double=random.randint(1, 2)),
            "Single": BedTypes(single=random.randint(1, 2)),
        }

        room_category = [
            "Ocean View",
            "Garden View",
            "City View",
            "Run of the House",
            "Superior Room",
            "Deluxe Room",
            "Junior Suite",
            "Prestige Suite",
        ]

        room_types = []
        for i in range(random.randint(1, 4)):
            code = random_string(6).upper()
            bed_type = random.choice([x for x in bed_types.keys()])
            category = random.choice(room_category)
            room_type_name = f"{bed_type} Bed {category}"
            amenities = self._sample_enum(Amenity)
            photos = self._get_photos(code)

            description = f"{category} room with a {bed_type.lower()} bed"
            rate_plans = self._generate_rate_plans()
            room_type = RoomType(
                code=code,
                name=room_type_name,
                description=description,
                amenities=amenities,
                photos=photos,
                capacity=RoomOccupancy(random.randint(2, 3), random.randint(0, 2)),
                bed_types=bed_types[bed_type],
            )

            room_type.rates = self._generate_room_rates(search_request, room_type, rate_plans)
            room_types.append(room_type)

        return room_types

    @staticmethod
    def _generate_rate_plans():
        rate_plan_def = {
            "Resort Package": {
                "Amenities": [Amenity.FREE_WIFI],
                "Cancellation": CancellationPolicy("Non Refundable", datetime.now(), ""),
            },
            "Free Continental Breakfast": {
                "Amenities": [Amenity.FREE_BREAKFAST],
                "Cancellation": CancellationPolicy("Non_Refundable", datetime.now(), ""),
            },
            "Refundable": {
                "Amenities": [],
                "Cancellation": CancellationPolicy("Refundable Up to 24 Hours", datetime.now(), ""),
            },
        }

        rate_plans = []
        rate_plan_types = list(rate_plan_def)
        for i in range(random.randint(1, len(rate_plan_types))):
            rate_plan_type = rate_plan_types[i]
            code = random_string(3).upper()
            rate_plan_amenities = rate_plan_def[rate_plan_type]["Amenities"]
            cancellation = rate_plan_def[rate_plan_type]["Cancellation"]
            rate_plans.append(RatePlan(code, rate_plan_type, rate_plan_type, rate_plan_amenities, cancellation))

        return rate_plans

    @staticmethod
    def _generate_room_rates(search_request: BaseHotelSearch, room_type: RoomType, rate_plan_types: List[RatePlan]):
        room_rates = []
        for i in range(len(rate_plan_types)):
            rate_plan = rate_plan_types[i]

            description = f"{room_type.name} {rate_plan.name}"
            room_nights = (search_request.end_date - search_request.start_date).days
            total_rate = decimal.Decimal(round(random.random() * 1200, 2))
            total_tax_rate = decimal.Decimal(round(total_rate / 10, 2))
            total_base_rate = decimal.Decimal(total_rate - total_tax_rate)
            base_rate = decimal.Decimal(round(total_rate / room_nights, 2))
            tax_rate = decimal.Decimal(round(total_tax_rate / room_nights, 2))

            daily_rates = []
            for night in range(room_nights):
                rate_date = search_request.start_date + timedelta(days=night)
                daily_base_rate = Money(base_rate, "USD")
                daily_tax_rate = Money(tax_rate, "USD")
                daily_total_rate = Money(base_rate + tax_rate, "USD")
                daily_rates.append(DailyRate(rate_date, daily_base_rate, daily_tax_rate, daily_total_rate))

            room_rates.append(
                RoomRate(
                    description=description,
                    additional_detail=list(),
                    total_base_rate=Money(total_base_rate, "USD"),
                    total_tax_rate=Money(total_tax_rate, "USD"),
                    total=Money(total_rate, "USD"),
                    daily_rates=daily_rates,
                    rate_key=random_alphanumeric(5),
                    rate_type=RateType.BOOKABLE,
                )
            )

        return room_rates

    def _generate_hotel_details(self, city=None):
        hotel_brands = ["Marriott", "Westin", "St. Regis", "Hyatt", "Holiday Inn"]
        hotel_location = ["Oceanfront", "Beach", "Garden", "Boardwalk", "Downtown"]
        hotel_types = ["Suites", "Cottages", "Tower", "Villas", "Inn"]

        random_brand = random.choice(hotel_brands)
        random_location = random.choice(hotel_location)
        random_type = random.choice(hotel_types)

        hotel_name = f"{random_brand} {random_location} {random_type}"
        hotel_address = self._generate_address(city=city)
        hotel_code = random_string(5).upper()

        latitude = random.random() * 100
        longitude = random.random() * 100
        geolocation = GeoLocation(latitude, longitude)

        return HotelDetails(
            name=hotel_name,
            address=hotel_address,
            chain_code="1A",
            hotel_code=hotel_code,
            checkin_time="3PM",
            checkout_time="12PM",
            geolocation=geolocation,
            photos=[],
            amenities=[],
        )

    @staticmethod
    def _generate_address(city=None):
        cities = ["San Francisco", "New York", "Seattle", "Los Angeles", "Boston"]
        street_types = ["Street", "Way", "Place", "Loop", "Boulevard"]
        street_names = ["Market", "Park", "Broadway", "First", "Second"]
        random_address = random.randrange(1, 1000, 8)
        random_type = random.choice(street_types)
        random_name = random.choice(street_names)

        if city is None:
            city = random.choice(cities)

        random_street_address = f"{random_address} {random_name} {random_type}"

        return Address(city, "NA", "12345", "US", random_street_address)

    @staticmethod
    def _sample_enum(cls: Type[Enum]):
        members = [name for name in cls]
        return random.sample(members, random.randint(1, len(members)))

    @staticmethod
    def _get_photos(code):
        photos = []
        for i in range(random.randint(1, 10)):
            url = f"https://i.simplenight-api-278418.ue.r.appspot.com/i/{code}.{i}.jpg"
            photos.append(Image(url, ImageType.ROOM))

        return photos
