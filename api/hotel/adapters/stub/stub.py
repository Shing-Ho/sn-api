from datetime import datetime
from enum import Enum
import random
from typing import List, Type

from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotels import (
    HotelLocationSearch,
    HotelAdapterHotel,
    HotelSpecificSearch,
    HotelSearchResponse,
    RoomOccupancy,
    RoomType,
    Amenity,
    Image,
    ImageType,
    BedTypes,
    RatePlan, CancellationPolicy, HotelDetails, HotelAddress, GeoLocation,
)
from common.utils import random_string


class StubHotelAdapter(HotelAdapter):
    def search_by_location(self, search_request: HotelLocationSearch) -> List[HotelAdapterHotel]:
        pass

    def search_by_id(self, search_request: HotelSpecificSearch) -> HotelSearchResponse:
        hotel_code = random_string(5).upper()
        response = HotelSearchResponse(
            hotel_id=hotel_code,
            checkin_date=search_request.checkin_date,
            checkout_date=search_request.checkout_date,
            occupancy=RoomOccupancy(2, 2),
            room_types=self._generate_room_types(),
            rate_plans=self._generate_rate_plans(),
            room_rates=self._generate_room_rates(),
            hotel_details=self._generate_hotel_details()
        )

        return response

    def details(self, *args):
        pass

    def _generate_room_types(self):
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
            room_type_name = f"{bed_type} {category}"
            amenities = self._sample_enum(Amenity)
            photos = self._get_photos(code)

            description = f"Beautiful {category} room with a {bed_type.lower()} bed"
            room_type = RoomType(
                code=code,
                name=room_type_name,
                description=description,
                amenities=amenities,
                photos=photos,
                capacity=RoomOccupancy(random.randint(2, 3), random.randint(0, 2)),
                bed_types=bed_types[bed_type],
            )
            room_types.append(room_type)

        return room_types

    @staticmethod
    def _generate_rate_plans():
        rate_plan_def = {
            "Resort Package": {
                "Amenities": [Amenity.FREE_WIFI],
                "Cancellation": CancellationPolicy("Non Refundable", datetime.now(), "")
            },
            "Free Continental Breakfast": {
                "Amenities": [Amenity.FREE_BREAKFAST],
                "Cancellation": CancellationPolicy("Non_Refundable", datetime.now(), ""),
            },
            "Refundable": {
                "Amenities": [],
                "Cancellation": CancellationPolicy("Refundable Up to 24 Hours", datetime.now(), "")
            }
        }

        rate_plans = []
        rate_plan_types = list(rate_plan_def)
        for i in range(random.randint(1, len(rate_plan_types))):
            code = random_string(3).upper()
            rate_plan_type = rate_plan_types[i]
            rate_plan_amenities = rate_plan_def[rate_plan_type]["Amenities"]
            cancellation = rate_plan_def[rate_plan_type]["Cancellation"]
            rate_plans.append(RatePlan(code, rate_plan_type, rate_plan_type, rate_plan_amenities, cancellation))

        return rate_plans

    def _generate_room_rates(self):
        return []

    def _generate_hotel_details(self, city=None):
        hotel_brands = ["Marriott", "Westin", "St. Regis", "Hyatt", "Holiday Inn"]
        hotel_location = ["Oceanfront", "Beach", "Gardens", "Boardwalk", "Downtown"]
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

        return HotelDetails(hotel_name, hotel_address, "1A", hotel_code, "3PM", "12PM", [], geolocation)

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

        return HotelAddress(city, "NA", "12345", "US", random_street_address)

    @staticmethod
    def _sample_enum(cls: Type[Enum]):
        members = [name for name in cls]
        return random.sample(members, random.randint(1, len(members)))

    @staticmethod
    def _get_photos(code):
        photos = []
        for i in range(random.randint(1, 10)):
            url = f"https://i.simplenight-api-278418.ue.r.appspot.com/i/{code}.i.jpg"
            photos.append(Image(url, ImageType.ROOM))

        return photos
