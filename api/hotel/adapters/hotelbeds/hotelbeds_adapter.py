from datetime import datetime
from decimal import Decimal
from typing import List, Any, Dict, Union

from api import logger
from api.hotel.adapters.hotelbeds.hotelbeds_common_models import (
    get_language_mapping,
)
from api.hotel.adapters.hotelbeds.hotelbeds_amenity_mappings import get_simplenight_amenity_mappings
from api.hotel.adapters.hotelbeds.hotelbeds_info import HotelbedsInfo
from api.hotel.adapters.hotelbeds.hotelbeds_transport import HotelbedsTransport
from api.hotel.adapters.hotel_adapter import HotelAdapter
from api.hotel.models.adapter_models import (
    AdapterLocationSearch,
    AdapterBaseSearch,
    AdapterHotelSearch,
    AdapterCancelRequest,
    AdapterCancelResponse,
    AdapterHotelBatchSearch,
)
from api.hotel.models.booking_model import (
    HotelBookingRequest,
    Reservation,
    Locator,
)
from api.hotel.models.hotel_api_model import (
    HotelDetails,
    AdapterHotel,
    RoomType,
    RatePlan,
    CancellationPolicy,
    CancellationSummary,
)
from api.hotel.models.hotel_common_models import (
    RoomOccupancy,
    Address,
    RateType,
    Money,
    RoomRate,
)
from api.view.exceptions import AvailabilityException, BookingException, AvailabilityErrorCode, BookingErrorCode


class HotelbedsAdapter(HotelAdapter):
    def __init__(self, transport=None):
        self.transport = transport
        if self.transport is None:
            self.transport = HotelbedsTransport(test_mode=True)

        self.adapter_info = HotelbedsInfo()
        self.provider = self.adapter_info.get_or_create_provider_id()

    def search_by_location(self, search: AdapterLocationSearch) -> List[AdapterHotel]:
        request = self._create_location_search(search)

        response = self.transport.hotels(**request)

        return self._normalize_hotels_search(search, response)

    def _create_location_search(self, search: AdapterLocationSearch):
        # TODO: get destination code from location id

        return {**self._create_base_search(search), "destination": {"code": "MCO"}}

    def _create_hotel_search(self, search: AdapterHotelSearch):
        return {**self._create_base_search(search), "hotels": {"hotel": [search.provider_hotel_id]}}

    def _create_hotel_batch_search(self, search: AdapterHotelBatchSearch):
        return {**self._create_base_search(search), "hotels": {"hotel": search.provider_hotel_ids}}

    @staticmethod
    def _create_base_search(search: AdapterBaseSearch):
        params = {
            "stay": {
                "checkIn": search.start_date.strftime("%Y-%m-%d"),
                "checkOut": search.end_date.strftime("%Y-%m-%d"),
            },
            "language": get_language_mapping(search.language),
            "occupancies": [
                {
                    "adults": search.occupancy.adults,
                    "children": search.occupancy.children,
                    "rooms": search.occupancy.num_rooms,
                }
            ],
            "filter": {"maxHotels": 120},
        }

        if search.currency:
            params["currency"] = search.currency

        return params

    def _normalize_hotels_search(self, search, response):
        if "error" in response or response["hotels"]["total"] == 0:
            if "error" in response:
                raise AvailabilityException(
                    detail=response["error"]["message"], error_type=AvailabilityErrorCode.PROVIDER_ERROR
                )
            else:
                return []

        hotel_codes = list(map(lambda x: str(x["code"]), response["hotels"]["hotels"]))
        hotel_details = self._details(hotel_codes, search.language)
        hotel_details_map = {x["code"]: x for x in hotel_details["hotels"]}
        hotels = list(
            map(
                lambda result: self._create_hotel_from_response(search, result, hotel_details_map[result["code"]]),
                response["hotels"]["hotels"],
            )
        )

        return hotels

    def _details(self, hotel_codes: Union[List[str], str], language: str):
        if isinstance(hotel_codes, list):
            hotel_codes = str.join(",", hotel_codes)

        params = {
            "language": get_language_mapping(language),
            "codes": hotel_codes,
            "fields": "all",
        }

        response = self.transport.hotel_content(**params)

        return response

    def _create_hotel_from_response(self, search, hotel_response, detail):
        room_types = self._create_room_types(hotel_response)
        rate_plans = self._create_rate_plans(hotel_response)
        room_rates = self._create_room_rates(hotel_response)
        hotel_details = self._create_hotel_details(detail)

        return AdapterHotel(
            provider=HotelbedsInfo.name,
            hotel_id=hotel_response["code"],
            start_date=search.start_date,
            end_date=search.end_date,
            occupancy=search.occupancy,
            room_types=room_types,
            rate_plans=rate_plans,
            room_rates=room_rates,
            hotel_details=hotel_details,
        )

    def search_by_id_batch(self, search: AdapterHotelBatchSearch) -> List[AdapterHotel]:
        request = self._create_hotel_search(search)

        response = self.transport.hotels(**request)

        return self._normalize_hotels_search(search, response)

    def search_by_id(self, search: AdapterHotelSearch) -> AdapterHotel:
        request = self._create_hotel_batch_search(search)

        response = self.transport.hotels(**request)

        return self._normalize_hotels_search(search, response)[0]

    def details(self, *args) -> HotelDetails:
        pass

    def recheck(self, room_rate: RoomRate) -> RoomRate:
        verified_hotel = self._recheck_request(room_rate)
        room_type_code = verified_hotel["hotel"]["rooms"][0]["code"]
        return self._create_room_rate(verified_hotel["hotel"]["rooms"][0]["rates"][0], room_type_code)

    def booking(self, book_request: HotelBookingRequest) -> Reservation:
        request = {
            "holder": {"name": book_request.customer.first_name, "surname": book_request.customer.last_name},
            "clientReference": book_request.transaction_id,
            "remark": "No remark",
            "rooms": [
                {
                    "rakeKey": book_request.room_code,
                    "paxes": [
                        {
                            "roomId": 1,
                            "type": "AD",
                            "name": book_request.customer.first_name,
                            "surname": book_request.customer.last_name,
                        }
                    ],
                }
            ],
        }

        response = self.transport.booking(request)
        if response is None:
            raise BookingException(f"Error During Booking")

        if "error" in response:
            error_message = response["error"]
            if "message" in error_message:
                error_message = error_message["message"]
            raise BookingException(f"Error During Booking: {error_message}")

        hotelbeds_room_rate = response["booking"]["hotel"]["rooms"][0]["rates"][0]
        room_rate = self._create_room_rate(hotelbeds_room_rate, room_type_code=book_request.room_code)

        return Reservation(
            locator=Locator(id=response["booking"]["reference"]),
            hotel_locator=None,
            hotel_id=book_request.hotel_id,
            checkin=datetime.strptime(response["booking"]["hotel"]["checkIn"], "%Y-%m-%d").date(),
            checkout=datetime.strptime(response["booking"]["hotel"]["checkOut"], "%Y-%m-%d").date(),
            customer=book_request.customer,
            traveler=book_request.traveler,
            room_rate=room_rate,
            cancellation_details=[],
        )

    def cancel(self, cancel_request: AdapterCancelRequest) -> AdapterCancelResponse:
        request = {"cancellationFlag": "CANCELLATION", "language": cancel_request.language}
        response = self.transport.booking_cancel(cancel_request.hotel_id, request)

        if response is None:
            raise BookingException(f"Error During Booking Cancel")

        if "error" in response:
            error_message = response["error"]
            if "message" in error_message:
                error_message = error_message["message"]
            raise BookingException(f"Error During Booking Cancel: {error_message}")

        if response["result"]["status"] != "CANCELLED":
            logger.error(f"Could not cancel booking {cancel_request}: {response}")
            raise BookingException(BookingErrorCode.CANCELLATION_FAILURE, "Could not cancel booking")

        return AdapterCancelResponse(is_cancelled=True)

    def get_image_url(self, path):
        return self._get_image_base_url() + path

    @staticmethod
    def _get_image_base_url():
        return "http://photos.hotelbeds.com/giata/bigger/"

    @classmethod
    def factory(cls, test_mode=True):
        return HotelbedsAdapter(HotelbedsTransport(test_mode=test_mode))

    @classmethod
    def get_provider_name(cls):
        return HotelbedsInfo.name

    @staticmethod
    def _create_room_types(hotel_response):
        room_types = []
        for room in hotel_response["rooms"]:
            adults = max(x["adults"] for x in room["rates"])
            children = max(x["children"] for x in room["rates"])
            children = max(x["children"] for x in room["rates"])
            occupancy = RoomOccupancy(adults=adults, children=children)
            room_type = RoomType(
                code=room["code"],
                name=room["name"],
                description=None,
                amenities=[],
                photos=[],
                capacity=occupancy,
                bed_types=None,
                unstructured_policies=None,
            )

            room_types.append(room_type)

        return room_types

    def _create_rate_plans(self, hotel_response):
        rate_plan = RatePlan(
            code="temporary-scaffolding",
            name="Temporary Rate Plan Name",
            description="This will be removed when rate plan refactor is complete",
            amenities=[],
            cancellation_policy=CancellationPolicy(summary=CancellationSummary.FREE_CANCELLATION),
        )

        return [rate_plan]

    def _create_room_rates(self, hotel_response):
        room_rates = []
        for room in hotel_response["rooms"]:
            for rate in room["rates"]:
                room_rates.append(self._create_room_rate(rate, room["code"], hotel_response["currency"]))

        return room_rates

    def _create_room_rate(self, rate: Dict[Any, Any], room_type_code: str, currency="USD"):
        net_amount = rate["net"]
        if net_amount is None:
            net_amount = Decimal("0.0")

        total_base_rate = Money(amount=net_amount, currency=currency)
        total_taxes = 0
        if "taxes" in rate:
            total_taxes = sum(x["amount"] for x in rate["taxes"]["taxes"] if x["amount"] is not None)

        total_tax_rate = Money(amount=total_taxes, currency=currency)
        total_amount = total_base_rate.amount + total_tax_rate.amount
        total_rate = Money(amount=total_amount, currency=currency)

        occupancy = RoomOccupancy(adults=rate["adults"], children=rate["children"], num_rooms=rate["rooms"])

        rate_type = RateType.BOOKABLE
        if "rateType" in rate:
            rate_type = self._get_rate_type(rate["rateType"])

        return RoomRate(
            code=rate["rateKey"] or room_type_code,
            rate_plan_code="temporary-scaffolding",
            room_type_code=room_type_code,
            rate_type=rate_type,
            total_base_rate=total_base_rate,
            total_tax_rate=total_tax_rate,
            total=total_rate,
            maximum_allowed_occupancy=occupancy,
        )

    @staticmethod
    def _get_rate_type(rate_type: str):
        if rate_type == "RECHECK":
            return "RECHECK"

        return "BOOKABLE"

    @staticmethod
    def _create_hotel_details(detail):
        if detail is None:
            return None

        facility_codes = set(x["facilityCode"] for x in detail["facilities"] or {})
        amenities = get_simplenight_amenity_mappings(facility_codes)

        address = Address(
            city=detail["city"]["content"],
            province=detail["stateCode"],
            postal_code=detail["postalCode"],
            country=detail["countryCode"],
            address1=detail["address"]["content"],
        )

        hotel_description = ""
        if detail["description"]:
            hotel_description = detail["description"]["content"]

        return HotelDetails(
            name=detail["name"]["content"],
            address=address,
            chain_code=detail["chainCode"],
            hotel_code=str(detail["code"]),
            checkin_time=None,
            checkout_time=None,
            amenities=list(amenities),
            star_rating=HotelbedsAdapter._get_star_rating(detail["categoryCode"]),
            property_description=hotel_description,
        )

    def _recheck_request(self, room_rate: RoomRate):
        request = {"rooms": [{"rateKey": room_rate.code}]}

        response = self.transport.checkrates(**request)

        return response

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
