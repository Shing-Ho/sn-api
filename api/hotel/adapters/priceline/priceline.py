import uuid
from decimal import Decimal
from enum import Enum
from typing import Union, List

from api import logger
from api.booking.booking_model import HotelBookingRequest
from api.common.models import RoomRate, RoomOccupancy, Money, RateType, Address
from api.hotel.adapters.priceline.priceline_info import PricelineInfo
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import (
    HotelDetails,
    HotelSpecificSearch,
    CrsHotel,
    HotelLocationSearch,
    RoomType,
    RatePlan,
    CancellationPolicy,
    CancellationSummary, GeoLocation,
)
from api.view.exceptions import AvailabilityException


class PricelineAdapter(HotelAdapter):
    def __init__(self, transport=None):
        self.transport = transport
        if self.transport is None:
            self.transport = PricelineTransport(test_mode=True)

    def search_by_location(self, search_request: HotelLocationSearch) -> List[CrsHotel]:
        priceline_request = self._create_city_search(search_request)
        logger.info(f"Initiating Priceline City Express Search: {priceline_request}")

        response = self.transport.hotel_express(**priceline_request)
        results = self._check_hotel_express_response_and_get_results(response)

        crs_hotels = list(map(lambda result: self._create_crs_hotel_from_response(search_request, result), results))
        return crs_hotels

    def search_by_id(self, search_request: HotelSpecificSearch) -> CrsHotel:
        pass

    def details(self, *args) -> HotelDetails:
        pass

    def booking(self, book_request: HotelBookingRequest):
        pass

    def recheck(self, room_rates: Union[RoomRate, List[RoomRate]]) -> List[RoomRate]:
        pass

    @staticmethod
    def _create_city_search(search_request: HotelLocationSearch):
        params = {
            "check_in": search_request.start_date,
            "check_out": search_request.end_date,
            "adults": search_request.occupancy.adults,
            "children": search_request.occupancy.children,
            "city_id": search_request.location_name,
        }

        if search_request.currency:
            params["currency"] = search_request.currency

        return params

    @staticmethod
    def _check_hotel_express_response_and_get_results(response):
        if response is None or "getHotelExpress.Results" not in response:
            raise AvailabilityException(code=PricelineErrorCodes.GENERIC_ERROR, detail="Could not retrieve response")

        results = response["getHotelExpress.Results"]
        if "error" in results:
            error_message = results["error"]["status"]
            raise AvailabilityException(code=PricelineErrorCodes.AVAILABILITY_ERROR, detail=error_message)

        return results["results"]["hotel_data"]

    def _create_crs_hotel_from_response(self, search, hotel_response):
        room_types = self._create_room_types(hotel_response)
        rate_plans = self._create_rate_plans(hotel_response)
        room_rates = self._create_room_rates(hotel_response, rate_plans)
        hotel_details = self._create_hotel_details(hotel_response)

        return CrsHotel(
            crs=PricelineInfo.name,
            hotel_id=hotel_response["id"],
            start_date=search.start_date,
            end_date=search.end_date,
            occupancy=search.occupancy,
            room_types=room_types,
            rate_plans=rate_plans,
            room_rates=room_rates,
            hotel_details=hotel_details,
        )

    @staticmethod
    def _create_hotel_details(hotel_data):
        address_response = hotel_data["address"]
        address = Address(
            city=address_response["city_name"],
            province=address_response["state_code"],
            country=address_response["country_code"],
            address1=address_response["address_line_one"],
            postal_code=address_response["zip"],
        )

        return HotelDetails(
            name=hotel_data["name"],
            address=address,
            hotel_code=hotel_data["id"],
            checkin_time=None,
            checkout_time=None,
            photos=[],
            amenities=[],
            geolocation=GeoLocation(hotel_data["geo"]["latitude"], hotel_data["geo"]["longitude"]),
            chain_code=hotel_data["hotel_chain"]["chain_codes_t"],
            star_rating=hotel_data["star_rating"],
            property_description=hotel_data["hotel_description"]
        )

    @staticmethod
    def _create_room_rates(hotel_response, rate_plans):
        room_rates = []
        for room in hotel_response["room_data"]:
            for rate in room["rate_data"]:
                price_details = rate["price_details"]
                display_currency = price_details["display_currency"]
                rate = RoomRate(
                    code=rate["ppn_bundle"],
                    room_type_code=rate["room_id"],
                    rate_plan_code=rate_plans[0].code,
                    maximum_allowed_occupancy=RoomOccupancy(adults=rate["occupancy_limit"]),
                    total_base_rate=Money(Decimal(price_details["display_sub_total"]), display_currency),
                    total_tax_rate=Money(Decimal(price_details["display_taxes"]), display_currency),
                    total=Money(Decimal(price_details["display_total"]), display_currency),
                    rate_type=RateType.BOOKABLE,
                )

                room_rates.append(rate)

        return room_rates

    @staticmethod
    def _create_rate_plans(hotel_response):
        """
        Currently, we only support cancellable/non-cancellable rate plans.
        Priceline rooms are all non-cancellable.  So we return one rate plan.
        """

        rate_plans = []
        rate_plan = RatePlan(
            code=str(uuid.uuid4()),
            name="Non-Refundable",
            description="For the room type and rate that you've selected, you are not allowed to change or cancel "
            "your reservation",
            amenities=[],
            cancellation_policy=CancellationPolicy(summary=CancellationSummary.NON_REFUNDABLE),
        )

        rate_plans.append(rate_plan)
        return rate_plans

    @staticmethod
    def _create_room_types(hotel_response):
        """
        RoomTypes and Rate Plans, and Rates are returned together by Priceline.
        Priceline supports an alternative format, where room types are grouped together.
        See Here: https://developer.pricelinepartnernetwork.com/guides/id/room-id-grouping
        This is the format that the Simplenight front-end requires.  That is, each room type is returned
        with a price, the services/cancellation policies in supports, and rates, all together.
        However, this is not the format requested by Google, and not the format returned by other connectors.
        So we parse out room type details from the rate data.
        """

        # TODO: See if we have room photos in downloadable content
        room_types = []
        for room in hotel_response["room_data"]:
            rate_data = room["rate_data"][0]
            room_type = RoomType(
                code=rate_data["room_id"],
                name=rate_data["title"],
                description=rate_data["description"],
                amenities=[],
                photos=[],
                capacity=RoomOccupancy(adults=rate_data["occupancy_limit"]),
                bed_types=None,
            )

            room_types.append(room_type)

        return room_types


class PricelineErrorCodes(Enum):
    GENERIC_ERROR = 1
    AVAILABILITY_ERROR = 2
