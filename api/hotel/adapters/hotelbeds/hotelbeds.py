from typing import List, Union, Optional

from api import logger
from api.booking.booking_model import HotelBookingRequest
from api.common.models import RateType, RoomRate, Money
from api.hotel.adapters.hotelbeds.booking_models import (
    HotelBedsBookingRQ,
    HotelBedsBookingLeadTraveler,
    HotelBedsPax,
    HotelBedsBookingRoom,
    HotelBedsBookingRS,
)
from api.hotel.adapters.hotelbeds.common_models import (
    get_language_mapping,
    HotelBedsRateType,
    HotelBedsException,
    HOTELBEDS_AMENITY_MAPPING,
)
from api.hotel.adapters.hotelbeds.details_models import HotelBedsHotelDetailsRS, HotelBedsHotelDetail, HotelBedsAmenity
from api.hotel.adapters.hotelbeds.search_models import (
    HotelBedsSearchBuilder,
    HotelBedsAvailabilityRS,
    HotelBedsHotel,
    HotelBedsRoomRS,
    HotelBedsRoomRateRS,
    HotelBedsCheckRatesRQ,
    HotelBedsCheckRatesRoom,
    HotelBedsCheckRatesRS,
)
from api.hotel.adapters.hotelbeds.transport import HotelBedsTransport
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import (
    HotelSpecificSearch,
    HotelDetails,
    CrsHotel,
    HotelLocationSearch,
    Address,
    BaseHotelSearch,
    RoomOccupancy,
    RoomType,
)


class HotelBeds(HotelAdapter):
    CRS_NAME = "hotelbeds"

    def __init__(self, transport=None):
        if transport is None:
            transport = HotelBedsTransport()

        self.transport = transport

    def search_by_location(self, search_request: HotelLocationSearch) -> List[CrsHotel]:
        availability_results = self._search_by_location(search_request)
        if availability_results.results.total == 0:
            return []

        hotel_codes = list(map(lambda x: str(x.code), availability_results.results.hotels))
        hotel_details = self._details(hotel_codes, search_request.language)
        hotel_details_map = {x.code: x for x in hotel_details.hotels}

        hotels = []
        for hotel in availability_results.results.hotels:
            # TODO: Fix this static hotel code when we have hotel details data available
            hotel_details = None
            if hotel.code in hotel_details_map:
                hotel_details = hotel_details_map[hotel.code]

            hotel = self._create_hotel(search_request, hotel, hotel_details)
            hotels.append(hotel)

        return hotels

    def _search_by_location(self, search_request: HotelLocationSearch) -> HotelBedsAvailabilityRS:
        request = HotelBedsSearchBuilder.build(search_request)
        endpoint = self.transport.get_hotels_url()
        response = self.transport.post(endpoint, request)

        if response.ok:
            results = response.json()
            return HotelBedsAvailabilityRS.Schema().load(results)

        logger.error(f"Error searching HotelBeds (status_code={response.status_code}): {response.text}")

    def search_by_id(self, search_request: HotelSpecificSearch) -> CrsHotel:
        pass

    def details(self, hotel_codes: Union[List[str], str], language: str) -> List[HotelDetails]:
        hotel_details_response = self._details(hotel_codes, language)
        return list(map(self._create_hotel_details, hotel_details_response.hotels))

    def _details(self, hotel_codes: Union[List[str], str], language: str) -> HotelBedsHotelDetailsRS:
        if isinstance(hotel_codes, list):
            hotel_codes = str.join(",", hotel_codes)

        params = {
            "language": get_language_mapping(language),
            "codes": hotel_codes,
            "fields": "all",
        }

        url = self.transport.get_hotel_content_url()
        response = self.transport.get(url, params)

        if response.ok:
            return HotelBedsHotelDetailsRS.Schema().load(response.json())

        logger.error(f"Error retrieving hotel details (status_code={response.status_code}): {response.text}")

    def get_facilities_types(self):
        endpoint = self.transport.get_facilities_types_url()
        params = {
            "fields": "all",
            "from": 1,
            "to": 500,
        }

        response = self.transport.get(endpoint, params)
        if response.ok:
            return response.json()

        logger.error(response.text)
        raise HotelBedsException(f"Could not find facilities types ({response.status_code})")

    def get_categories(self):
        endpoint = self.transport.get_categories_types_url()
        params = {
            "fields": "all",
            "from": 1,
            "to": 500,
        }

        response = self.transport.get(endpoint, params)
        if response.ok:
            return response.json()

        logger.error(response.text)
        raise HotelBedsException(f"Could not find categories ({response.status_code})")

    def recheck(self, room_rates: Union[RoomRate, List[RoomRate]]) -> List[RoomRate]:
        verified_hotel = self._recheck_request(room_rates)
        return list(map(self._create_room_rate, verified_hotel.hotel.rooms[0].rates))

    def _recheck_request(self, room_rates: Union[RoomRate, List[RoomRate]]) -> HotelBedsCheckRatesRS:
        rooms_to_check = list(HotelBedsCheckRatesRoom(rate_key=x.rate_key) for x in room_rates)
        request = HotelBedsCheckRatesRQ(rooms=rooms_to_check)

        response = self.transport.post(self.transport.get_checkrates_url(), request)

        if not response.ok:
            raise HotelBedsException("Could not recheck price for booking")

        return HotelBedsCheckRatesRS.Schema().load(response.json())

    def booking(self, book_request: HotelBookingRequest) -> Optional[HotelBedsBookingRS]:
        self.transport.get_booking_url()

        lead_traveler = HotelBedsPax(1, "AD", book_request.customer.first_name, book_request.customer.last_name)

        rooms_to_book = []
        for room_rate in book_request.room_rates:
            booking_room = HotelBedsBookingRoom(rateKey=room_rate.rate_key, paxes=[lead_traveler])
            rooms_to_book.append(booking_room)

        booking_request = HotelBedsBookingRQ(
            holder=HotelBedsBookingLeadTraveler(
                name=book_request.customer.first_name, surname=book_request.customer.last_name
            ),
            clientReference=book_request.transaction_id,
            rooms=rooms_to_book,
        )

        response = self.transport.post(self.transport.get_booking_url(), booking_request)
        if not response.ok:
            logger.error({"message": "Error booking HotelBeds", "request": booking_request})
            logger.error(response.raw)
            raise HotelBedsException(f"Error During Booking: {response.raw}")

        return HotelBedsBookingRS.Schema().load(response.json())

    def get_image_url(self, path):
        return self._get_image_base_url() + path

    @staticmethod
    def _get_image_base_url():
        return "http://photos.hotelbeds.com/giata/bigger/"

    def _create_hotel(self, search: BaseHotelSearch, hotel: HotelBedsHotel, detail: HotelBedsHotelDetail) -> CrsHotel:

        room_types = list(map(lambda x: self._create_room_type(search, x), hotel.rooms))

        return CrsHotel(
            crs=self.CRS_NAME,
            hotel_id=str(hotel.code),
            start_date=search.start_date,
            end_date=search.end_date,
            occupancy=search.occupancy,
            room_types=room_types,
            hotel_details=self._create_hotel_details(detail),
        )

    def _create_room_type(self, search: BaseHotelSearch, hotelbeds_room: HotelBedsRoomRS):
        adults = max(x.adults for x in hotelbeds_room.rates)
        children = max(x.children for x in hotelbeds_room.rates)
        occupancy = RoomOccupancy(adults=adults, children=children)

        rates = list(map(lambda x: self._create_room_rate(x, search.currency), hotelbeds_room.rates))

        return RoomType(
            code=hotelbeds_room.code,
            name=hotelbeds_room.name,
            description=None,
            amenities=[],
            photos=[],
            capacity=occupancy,
            bed_types=None,
            unstructured_policies=None,
            rates=rates,
        )

    def _create_room_rate(self, rate: HotelBedsRoomRateRS, currency=None):
        total_base_rate = Money(rate.net, currency)
        total_taxes = 0
        if rate.taxes:
            total_taxes = sum(x.amount for x in rate.taxes.taxes if x.amount is not None)

        total_tax_rate = Money(total_taxes, currency)
        total_rate = Money(total_base_rate.amount + total_tax_rate.amount, currency)

        return RoomRate(
            rate_key=rate.rate_key,
            rate_type=self._get_rate_type(rate.rate_type),
            description="",
            additional_detail=[],
            total_base_rate=total_base_rate,
            total_tax_rate=total_tax_rate,
            total=total_rate,
        )

    @staticmethod
    def _get_rate_type(rate_type: HotelBedsRateType):
        if rate_type == HotelBedsRateType.RECHECK:
            return RateType.RECHECK

        return RateType.BOOKABLE

    @staticmethod
    def _create_hotel_details(detail: HotelBedsHotelDetail) -> Optional[HotelDetails]:
        if detail is None:
            return None

        facility_codes = set(x.facility_code for x in detail.amenities or {})
        amenities = set()
        for amenity, code in HOTELBEDS_AMENITY_MAPPING.items():
            if any(x for x in code if x in facility_codes):
                amenities.add(amenity)

        address = Address(
            city=detail.city.content,
            province=detail.state_code,
            postal_code=detail.postal_code,
            country=detail.country_code,
            address1=detail.address.content,
        )

        return HotelDetails(
            name=detail.name.content,
            address=address,
            chain_code=detail.chain_code,
            hotel_code=str(detail.code),
            checkin_time=None,
            checkout_time=None,
            amenities=list(amenities),
            star_rating=HotelBeds._get_star_rating(detail.category_code),
            property_description=detail.description.content,
        )

    @staticmethod
    def _get_star_rating(category_code):
        return {
            "1EST": 1,
            "2EST": 2,
            "3EST": 3,
            "4EST": 4,
            "5EST": 5,
            "6EST": 6,
            "H1_5": 1.5,
            "H2_5": 2.5,
            "H3_5": 3.5,
            "H4_5": 4.5,
        }.get(category_code, None)

    @staticmethod
    def _get_matching_amenities(hotelbeds_amenities: List[HotelBedsAmenity]):
        facility_codes = set(x.facility_code for x in hotelbeds_amenities or [])
        return {amenity for amenity, code in HOTELBEDS_AMENITY_MAPPING.items() if code in facility_codes}
