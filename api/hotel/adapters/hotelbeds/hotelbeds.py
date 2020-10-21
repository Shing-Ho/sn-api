from datetime import date
from decimal import Decimal
from typing import List, Union, Optional

from api import logger
from api.hotel.models.booking_model import HotelBookingRequest, Reservation, Locator
from api.common.models import RateType, RoomRate, Money
from api.hotel.adapters.hotelbeds.booking_models import (
    HotelBedsBookingRQ,
    HotelBedsBookingLeadTraveler,
    HotelBedsPax,
    HotelBedsBookingRoom,
    HotelBedsBookingRS,
    HotelBedsBookingRoomRateRS,
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
from api.hotel.models.hotel_api_model import (
    HotelDetails,
    AdapterHotel,
    Address,
    RoomOccupancy,
    RoomType,
    RatePlan,
    CancellationPolicy,
    CancellationSummary,
)
from api.hotel.models.adapter_models import AdapterLocationSearch, AdapterBaseSearch, AdapterHotelSearch, \
    AdapterCancelRequest, AdapterCancelResponse
from api.view.exceptions import AvailabilityException, AvailabilityErrorCode


class HotelBeds(HotelAdapter):
    PROVIDER_NAME = "hotelbeds"

    def __init__(self, transport=None):
        if transport is None:
            transport = HotelBedsTransport()

        self.transport = transport

    def search_by_location(self, search: AdapterLocationSearch) -> List[AdapterHotel]:
        availability_results = self._search_by_location(search)

        if availability_results.error or availability_results.results.total == 0:
            if availability_results.error:
                raise AvailabilityException(
                    detail=availability_results.error.message, error_type=AvailabilityErrorCode.PROVIDER_ERROR
                )
            else:
                return []

        hotel_codes = list(map(lambda x: str(x.code), availability_results.results.hotels))
        hotel_details = self._details(hotel_codes, search.language)
        hotel_details_map = {x.code: x for x in hotel_details.hotels}

        hotels = []
        for hotel in availability_results.results.hotels:
            # TODO: Fix this static hotel code when we have hotel details data available
            hotel_details = None
            if hotel.code in hotel_details_map:
                hotel_details = hotel_details_map[hotel.code]

            hotel = self._create_hotel(search, hotel, hotel_details)
            hotels.append(hotel)

        return hotels

    def _search_by_location(self, search_request: AdapterLocationSearch) -> HotelBedsAvailabilityRS:
        request = HotelBedsSearchBuilder.build(search_request)
        endpoint = self.transport.get_hotels_url()
        response = self.transport.post(endpoint, request)

        return HotelBedsAvailabilityRS.parse_raw(response.text)

    def search_by_id(self, search_request: AdapterHotelSearch) -> AdapterHotel:
        pass

    def details(self, hotel_codes: Union[List[str], str], language: str) -> List[HotelDetails]:
        hotel_details_response = self._details(hotel_codes, language)
        return list(map(self._create_hotel_details, hotel_details_response.hotels))

    def _details(self, hotel_codes: Union[List[str], str], language: str) -> Optional[HotelBedsHotelDetailsRS]:
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
            return HotelBedsHotelDetailsRS.parse_raw(response.text)

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

    def recheck(self, room_rate: RoomRate) -> RoomRate:
        verified_hotel = self._recheck_request(room_rate)
        room_type_code = verified_hotel.hotel.rooms[0].code
        return self._create_room_rate(verified_hotel.hotel.rooms[0].rates[0], room_type_code)

    def _recheck_request(self, room_rate: RoomRate) -> HotelBedsCheckRatesRS:
        room_to_check = HotelBedsCheckRatesRoom(rateKey=room_rate.code)
        request = HotelBedsCheckRatesRQ(rooms=[room_to_check])

        response = self.transport.post(self.transport.get_checkrates_url(), request)

        if not response.ok:
            raise HotelBedsException("Could not recheck price for booking")

        return HotelBedsCheckRatesRS.parse_raw(response.text)

    def booking(self, book_request: HotelBookingRequest) -> Reservation:
        # To book a Priceline room, we first need to do a contract lookup call
        # We use the price verification framework to test if the room prices are equivalent
        # Currently, we don't handle the case where they are not.

        lead_traveler = HotelBedsPax(
            roomId=1, type="AD", name=book_request.customer.first_name, surname=book_request.customer.last_name
        )

        room_code = book_request.room_code
        booking_room = HotelBedsBookingRoom(rateKey=room_code, paxes=[lead_traveler])

        booking_request = HotelBedsBookingRQ(
            holder=HotelBedsBookingLeadTraveler(
                name=book_request.customer.first_name, surname=book_request.customer.last_name
            ),
            clientReference=book_request.transaction_id,
            rooms=[booking_room],
            remark="No remark",
        )

        response = self.transport.post(self.transport.get_booking_url(), booking_request)
        if not response.ok:
            logger.error({"message": "Error booking HotelBeds", "request": booking_request})
            logger.error(response.text)
            raise HotelBedsException(f"Error During Booking: {response.text}")

        hotelbeds_booking_response: HotelBedsBookingRS = HotelBedsBookingRS.parse_raw(response.text)

        # TODO JLM: Parse checkin, checkout and room rate from HotelBeds booking response

        hotelbeds_room_rate = hotelbeds_booking_response.booking.hotel.rooms[0].rates[0]
        room_rate = self._create_room_rate(hotelbeds_room_rate, room_type_code=book_request.room_code)

        return Reservation(
            locator=Locator(id=hotelbeds_booking_response.booking.reference),
            hotel_locator=None,
            hotel_id=book_request.hotel_id,
            checkin=date(2000, 1, 1),
            checkout=date(2000, 1, 1),
            customer=book_request.customer,
            traveler=book_request.traveler,
            room_rate=room_rate,
            cancellation_details=[],
        )

    def cancel(self, cancel_request: AdapterCancelRequest) -> AdapterCancelResponse:
        raise NotImplemented("Cancel not implemented")

    def get_image_url(self, path):
        return self._get_image_base_url() + path

    @staticmethod
    def _get_image_base_url():
        return "http://photos.hotelbeds.com/giata/bigger/"

    def _create_hotel(
        self, search: AdapterBaseSearch, hotel: HotelBedsHotel, detail: HotelBedsHotelDetail
    ) -> AdapterHotel:

        room_types = list(map(lambda x: self._create_room_type(x), hotel.rooms))

        room_rates = []
        for room in hotel.rooms:
            for rate in room.rates:
                room_rates.append(self._create_room_rate(rate, room.code, hotel.currency))

        rate_plan = RatePlan(
            code="temporary-scaffolding",
            name="Temporary Rate Plan Name",
            description="This will be removed when rate plan refactor is complete",
            amenities=[],
            cancellation_policy=CancellationPolicy(summary=CancellationSummary.FREE_CANCELLATION),
        )

        return AdapterHotel(
            provider=self.PROVIDER_NAME,
            hotel_id=str(hotel.code),
            start_date=search.start_date,
            end_date=search.end_date,
            occupancy=search.occupancy,
            room_types=room_types,
            room_rates=room_rates,
            rate_plans=[rate_plan],
            hotel_details=self._create_hotel_details(detail),
        )

    @staticmethod
    def _create_room_type(hotelbeds_room: HotelBedsRoomRS):
        adults = max(x.adults for x in hotelbeds_room.rates)
        children = max(x.children for x in hotelbeds_room.rates)
        occupancy = RoomOccupancy(adults=adults, children=children)

        return RoomType(
            code=hotelbeds_room.code,
            name=hotelbeds_room.name,
            description=None,
            amenities=[],
            photos=[],
            capacity=occupancy,
            bed_types=None,
            unstructured_policies=None,
        )

    def _create_room_rate(
        self, rate: Union[HotelBedsBookingRoomRateRS, HotelBedsRoomRateRS], room_type_code: str, currency="USD"
    ):
        net_amount = rate.net
        if net_amount is None:
            net_amount = Decimal("0.0")

        total_base_rate = Money(amount=net_amount, currency=currency)
        total_taxes = 0
        if rate.taxes:
            total_taxes = sum(x.amount for x in rate.taxes.taxes if x.amount is not None)

        total_tax_rate = Money(amount=total_taxes, currency=currency)
        total_amount = total_base_rate.amount + total_tax_rate.amount
        total_rate = Money(amount=total_amount, currency=currency)

        occupancy = RoomOccupancy(adults=rate.adults, children=rate.children, num_rooms=rate.rooms)

        rate_type = RateType.BOOKABLE
        if isinstance(rate, HotelBedsRoomRateRS):
            rate_type = self._get_rate_type(rate.rate_type)

        return RoomRate(
            code=rate.rate_key or room_type_code,
            rate_plan_code="temporary-scaffolding",
            room_type_code=room_type_code,
            rate_type=rate_type,
            total_base_rate=total_base_rate,
            total_tax_rate=total_tax_rate,
            total=total_rate,
            maximum_allowed_occupancy=occupancy,
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

        hotel_description = ""
        if detail.description:
            hotel_description = detail.description.content

        return HotelDetails(
            name=detail.name.content,
            address=address,
            chain_code=detail.chain_code,
            hotel_code=str(detail.code),
            checkin_time=None,
            checkout_time=None,
            amenities=list(amenities),
            star_rating=HotelBeds._get_star_rating(detail.category_code),
            property_description=hotel_description,
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

    @classmethod
    def factory(cls, test_mode=True):
        return HotelBeds(HotelBedsTransport())

    @classmethod
    def get_provider_name(cls):
        return cls.PROVIDER_NAME
