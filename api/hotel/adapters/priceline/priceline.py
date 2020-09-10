import uuid
from decimal import Decimal
from enum import Enum
from typing import List, Any, Dict

from api import logger
from api.booking.booking_model import (
    HotelBookingRequest,
    Customer,
    Payment,
    HotelBookingResponse,
    Status,
    Reservation,
    Locator,
)
from api.common.models import RoomRate, RoomOccupancy, Money, RateType, Address
from api.common.request_context import get_request_context
from api.hotel.adapters.priceline.priceline_info import PricelineInfo
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.hotel_adapter import HotelAdapter
from api.hotel.hotel_model import (
    HotelDetails,
    HotelSpecificSearch,
    AdapterHotel,
    HotelLocationSearch,
    RoomType,
    RatePlan,
    CancellationPolicy,
    CancellationSummary,
    GeoLocation,
    BaseHotelSearch,
)
from api.view.exceptions import AvailabilityException, BookingException


class PricelineAdapter(HotelAdapter):
    def __init__(self, transport=None):
        self.transport = transport
        if self.transport is None:
            self.transport = PricelineTransport(test_mode=True)

    def search_by_location(self, search_request: HotelLocationSearch) -> List[AdapterHotel]:
        request = self._create_city_search(search_request)
        logger.info(f"Initiating Priceline City Express Search: {request}")

        response = self.transport.hotel_express(**request)
        hotel_results = self._check_hotel_express_response_and_get_results(response)

        hotels = list(map(lambda result: self._create_hotel_from_response(search_request, result), hotel_results))
        return hotels

    def search_by_id(self, search: HotelSpecificSearch) -> AdapterHotel:
        request = self._create_hotel_id_search(search)
        logger.info(f"Initiating Priceline Hotel Express Search: {request}")

        response = self.transport.hotel_express(**request)
        hotel_results = self._check_hotel_express_response_and_get_results(response)

        return self._create_hotel_from_response(search, hotel_results[0])

    def details(self, *args) -> HotelDetails:
        pass

    def room_details(self, ppn_bundle: str) -> RoomRate:
        params = {"ppn_bundle": ppn_bundle}
        response = self.transport.express_contract(**params)

        hotel_data = self._check_hotel_express_contract_response_and_get_results(response)[0]
        rate_plans = self._create_rate_plans()
        room_data = hotel_data["room_data"][0]
        rate_data = room_data["rate_data"][0]
        room_id = room_data["id"]

        return self._create_room_rate(room_id, rate_data, rate_plans[0])

    def booking(self, book_request: HotelBookingRequest) -> HotelBookingResponse:
        for rate in book_request.room_rates:
            params = self._create_booking_params(book_request.customer, book_request.payment, rate)
            response = self.transport.express_book(**params)

            if "getHotelExpress.Book" not in response:
                raise BookingException(PricelineErrorCodes.GENERIC_BOOKING_ERROR, response)

            results = response["getHotelExpress.Book"]["results"]
            if results["status"] != "Success":
                raise BookingException(PricelineErrorCodes.BOOKING_FAILURE, response)

            booking_data = results["book_data"]
            booking_locator = booking_data["itinerary"]["id"]
            hotel_locators = [
                Locator(id=room["confirmation_code"]) for room in booking_data["itinerary_details"]["room_data"]
            ]

            reservation = Reservation(
                locator=Locator(id=booking_locator),
                hotel_locator=hotel_locators,
                hotel_id=book_request.hotel_id,
                checkin=book_request.checkin,
                checkout=book_request.checkout,
                customer=book_request.customer,
                traveler=book_request.traveler,
                room_rates=book_request.room_rates,
            )

            return HotelBookingResponse(
                api_version=1,
                transaction_id=book_request.transaction_id,
                status=Status(True, "success"),
                reservation=reservation,
            )

    def recheck(self, room_rate: RoomRate) -> RoomRate:
        return self.room_details(room_rate.code)

    @staticmethod
    def _create_booking_params(customer: Customer, payment: Payment, rate: RoomRate):
        request_context = get_request_context()
        payment_card_params = payment.payment_card_parameters
        expires_string = f"{int(payment_card_params.expiration_month):02d}{payment_card_params.expiration_year}"
        return {
            "ppn_bundle": rate.code,
            "name_first": customer.first_name,
            "name_last": customer.last_name,
            "phone_number": customer.phone_number,
            "email": customer.email,
            "card_holder": f"{customer.first_name} {customer.last_name}",
            "address_line_one": payment.billing_address.address1,
            "address_city": payment.billing_address.city,
            "address_state_code": payment.billing_address.province,
            "country_code": payment.billing_address.country,
            "address_postal_code": payment.billing_address.postal_code,
            "card_type": payment_card_params.card_type.name,
            "card_number": payment_card_params.card_number,
            "expires": expires_string,
            "cvc_code": payment_card_params.cvv,
            "sid": request_context.get_request_id(),
        }

    def _create_hotel_id_search(self, search: HotelSpecificSearch):
        return {
            **self._create_base_search(search),
            "hotel_ids": search.hotel_id,
        }

    def _create_city_search(self, search: HotelLocationSearch):
        return {
            **self._create_base_search(search),
            "city_id": search.location_name,
        }

    @staticmethod
    def _create_base_search(search: BaseHotelSearch):
        params = {
            "check_in": search.start_date,
            "check_out": search.end_date,
            "adults": search.occupancy.adults,
            "children": search.occupancy.children,
        }

        if search.currency:
            params["currency"] = search.currency

        return params

    @staticmethod
    def _check_hotel_express_operation_response_and_get_results(response, operation):
        if response is None or operation not in response:
            raise AvailabilityException(code=PricelineErrorCodes.GENERIC_ERROR, detail="Could not retrieve response")

        results = response[operation]
        if "error" in results:
            error_message = results["error"]["status"]
            raise AvailabilityException(code=PricelineErrorCodes.AVAILABILITY_ERROR, detail=error_message)

        return results["results"]["hotel_data"]

    def _check_hotel_express_response_and_get_results(self, response):
        return self._check_hotel_express_operation_response_and_get_results(response, "getHotelExpress.Results")

    def _check_hotel_express_contract_response_and_get_results(self, response):
        return self._check_hotel_express_operation_response_and_get_results(response, "getHotelExpress.Contract")

    def _create_hotel_from_response(self, search, hotel_response):
        room_types = self._create_room_types(hotel_response)
        rate_plans = self._create_rate_plans()
        room_rates = self._create_room_rates(hotel_response, rate_plans)
        hotel_details = self._create_hotel_details(hotel_response)

        return AdapterHotel(
            provider=PricelineInfo.name,
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
            property_description=hotel_data["hotel_description"],
        )

    @staticmethod
    def _create_room_rate(room_id: str, rate_data: Dict[Any, Any], rate_plan) -> RoomRate:
        rate_code = PricelineAdapter.get_ppn_bundle_code(rate_data)
        price_details = rate_data["price_details"]
        display_currency = price_details["display_currency"]

        return RoomRate(
            code=rate_code,
            room_type_code=room_id,
            rate_plan_code=rate_plan.code,
            maximum_allowed_occupancy=RoomOccupancy(adults=rate_data["occupancy_limit"]),
            total_base_rate=Money(Decimal(price_details["display_sub_total"]), display_currency),
            total_tax_rate=Money(Decimal(price_details["display_taxes"]), display_currency),
            total=Money(Decimal(price_details["display_total"]), display_currency),
            rate_type=RateType.BOOKABLE,
        )

    @staticmethod
    def get_ppn_bundle_code(rate_data):
        if "ppn_book_bundle" in rate_data:
            rate_code = rate_data["ppn_book_bundle"]
        else:
            rate_code = rate_data["ppn_bundle"]
        return rate_code

    def _create_room_rates(self, hotel_response, rate_plans):
        room_rates = []
        for room in hotel_response["room_data"]:
            for rate in room["rate_data"]:
                room_id = room["id"]
                room_rates.append(self._create_room_rate(room_id, rate, rate_plans[0]))

        return room_rates

    @staticmethod
    def _create_rate_plans():
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
                code=room["id"],
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
    GENERIC_BOOKING_ERROR = 3
    BOOKING_FAILURE = 4
