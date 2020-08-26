import decimal
import random
import uuid
from datetime import timedelta
from typing import List, Union

from api.booking.booking_model import Reservation, HotelBookingRequest, HotelBookingResponse, Locator, Status
from api.common.models import RateType, RoomRate, DailyRate, Money
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import (
    HotelLocationSearch,
    CrsHotel,
    RoomOccupancy,
    RoomType,
    Image,
    ImageType,
    BedTypes,
    CancellationPolicy,
    HotelDetails,
    Address,
    GeoLocation,
    RatePlan,
    BaseHotelSearch,
    HotelSpecificSearch,
    SimplenightAmenities,
    CancellationSummary,
)
from api.tests.utils import random_alphanumeric
from common.utils import random_string


class StubHotelAdapter(HotelAdapter):
    """Stub Hotel Adapter, generates fakes data, for testing purposes"""

    CRS_NAME = "stub"

    def search_by_location(self, search_request: HotelLocationSearch) -> List[CrsHotel]:
        num_hotels_to_return = random.randint(10, 50)

        return [self.search_by_id(search_request) for _ in range(num_hotels_to_return)]

    def search_by_id(self, search_request: Union[BaseHotelSearch, HotelSpecificSearch]) -> CrsHotel:
        hotel_code = random_string(5).upper()
        if isinstance(search_request, HotelSpecificSearch) and search_request.hotel_id:
            hotel_code = search_request.hotel_id

        room_types = self._generate_room_types()
        rate_plans = self._generate_rate_plans(search_request)
        room_rates = self._generate_room_rates(search_request, room_types, rate_plans)

        response = CrsHotel(
            crs=self.CRS_NAME,
            hotel_id=hotel_code,
            start_date=search_request.start_date,
            end_date=search_request.end_date,
            occupancy=RoomOccupancy(adults=2, children=2),
            room_types=room_types,
            rate_plans=rate_plans,
            room_rates=room_rates,
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
            room_type_name = f"{bed_type} Bed {category}"
            amenities = random.sample(list(SimplenightAmenities), random.randint(1, 2))
            photos = self._get_photos(code)

            description = f"{category} room with a {bed_type.lower()} bed"
            room_type = RoomType(
                code=code,
                name=room_type_name,
                description=description,
                amenities=amenities,
                photos=photos,
                capacity=RoomOccupancy(adults=random.randint(0, 2), children=2),
                bed_types=bed_types[bed_type],
            )

            room_types.append(room_type)

        return room_types

    @staticmethod
    def _generate_rate_plans(hotel_search: BaseHotelSearch):
        refundable_rate_plan = RatePlan(
            name="Free Cancellation",
            code=random_alphanumeric(8),
            description=f"Free Cancellation allowed without charge before {hotel_search.start_date - timedelta(days=14)}",
            amenities=[SimplenightAmenities.WIFI],
            cancellation_policy=CancellationPolicy(
                summary=CancellationSummary.FREE_CANCELLATION,
                cancellation_deadline=hotel_search.start_date - timedelta(days=14),
            ),
        )

        non_refundable_rate_plan = RatePlan(
            name="Lowest Rate",
            code=random_alphanumeric(8),
            description=f"Lowest available rate (non-refundable)",
            amenities=[],
            cancellation_policy=CancellationPolicy(summary=CancellationSummary.NON_REFUNDABLE),
        )

        return [refundable_rate_plan, non_refundable_rate_plan]

    @staticmethod
    def _generate_room_rates(
        search_request: BaseHotelSearch, room_types: List[RoomType], rate_plan_types: List[RatePlan]
    ):
        room_rates = []
        for room_types in room_types:
            for rate_plan in rate_plan_types:
                room_nights = (search_request.end_date - search_request.start_date).days
                total_rate = round(decimal.Decimal(random.random() * 1200), 2)
                total_tax_rate = round(decimal.Decimal(total_rate / 10), 2)
                total_base_rate = decimal.Decimal(total_rate - total_tax_rate)
                base_rate = round(decimal.Decimal(total_rate / room_nights), 2)
                tax_rate = round(decimal.Decimal(total_tax_rate / room_nights), 2)

                daily_rates = []
                for night in range(room_nights):
                    rate_date = search_request.start_date + timedelta(days=night)
                    daily_base_rate = Money(base_rate, "USD")
                    daily_tax_rate = Money(tax_rate, "USD")
                    daily_total_rate = Money(base_rate + tax_rate, "USD")
                    daily_rates.append(DailyRate(rate_date, daily_base_rate, daily_tax_rate, daily_total_rate))

                room_rates.append(
                    RoomRate(
                        code=random_alphanumeric(8),
                        room_type_code=room_types.code,
                        rate_plan_code=rate_plan.code,
                        maximum_allowed_occupancy=RoomOccupancy(adults=2, children=2),
                        total_base_rate=Money(total_base_rate, "USD"),
                        total_tax_rate=Money(total_tax_rate, "USD"),
                        total=Money(total_rate, "USD"),
                        daily_rates=daily_rates,
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

        star_rating = random.choice([2, 2.5, 3, 3.5, 4, 4.5, 5])

        amenities = random.sample(list(SimplenightAmenities), random.randint(3, 10))

        return HotelDetails(
            name=hotel_name,
            address=hotel_address,
            chain_code="1A",
            hotel_code=hotel_code,
            checkin_time="3PM",
            checkout_time="12PM",
            geolocation=geolocation,
            photos=[],
            amenities=amenities,
            star_rating=star_rating,
            property_description=self._get_property_description(),
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

        return Address(city=city, province="CA", country="US", postal_code="12345", address1=random_street_address)

    @staticmethod
    def _get_photos(code):
        photos = []
        for i in range(random.randint(1, 10)):
            url = f"https://i.simplenight-api-278418.ue.r.appspot.com/i/{code}.{i}.jpg"
            photos.append(Image(url, ImageType.ROOM))

        return photos

    @staticmethod
    def _get_property_description():
        return (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore "
            "et dolore magna aliqua. Eros in cursus turpis massa. Libero nunc consequat interdum varius sit amet "
            "mattis vulputate. Tristique magna sit amet purus gravida. Fermentum posuere urna nec tincidunt "
            "praesent semper. Vitae semper quis lectus nulla. Dui nunc mattis enim ut tellus elementum sagittis "
            "vitae et. Purus viverra accumsan in nisl. Pharetra sit amet aliquam id diam. Vulputate sapien nec "
            "sagittis aliquam malesuada. Bibendum enim facilisis gravida neque. "
        )
