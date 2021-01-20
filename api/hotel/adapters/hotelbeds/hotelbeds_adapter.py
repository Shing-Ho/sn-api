from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import List, Any, Dict, Union

import pytz
from dateutil.relativedelta import relativedelta

from api import logger
from api.hotel.adapters.hotel_adapter import HotelAdapter
from api.hotel.adapters.hotelbeds.hotelbeds_amenity_mappings import get_simplenight_amenity_mappings
from api.hotel.adapters.hotelbeds.hotelbeds_common_models import get_language_mapping
from api.hotel.adapters.hotelbeds.hotelbeds_info import HotelbedsInfo
from api.hotel.adapters.hotelbeds.hotelbeds_transport import HotelbedsTransport
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
    HotelReservation,
    Locator,
)
from api.hotel.models.hotel_api_model import (
    HotelDetails,
    AdapterHotel,
    RoomType,
    RatePlan,
    CancellationPolicy,
    CancellationSummary,
    CancellationDetails,
    Image,
    ImageType,
)
from api.hotel.models.hotel_common_models import (
    Address,
    RoomOccupancy,
    Money,
    RoomRate,
    HotelReviews,
)
from api.models.models import ProviderImages, ProviderHotel
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
        hotel_results = self._check_hotels_response_and_get_results(response)

        hotels = list(map(lambda result: self._create_hotel_from_response(search, result), hotel_results,))
        self._enrich_hotels(hotels)

        return hotels

    def _create_location_search(self, search: AdapterLocationSearch):
        location = self.get_provider_location(search)
        location_code = location.provider_code

        return {**self._create_base_search(search), "destination": {"code": location_code}}

    def _create_hotel_id_search(self, search: AdapterHotelSearch):
        return {**self._create_base_search(search), "hotels": {"hotel": [search.provider_hotel_id]}}

    def _create_hotel_id_batch_search(self, search: AdapterHotelBatchSearch):
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

    def _details(self, hotel_response, language: str):
        hotel_codes = list(map(lambda x: str(x.code), hotel_response))
        if isinstance(hotel_codes, list):
            hotel_codes = str.join(",", hotel_codes)

        params = {
            "language": get_language_mapping(language),
            "codes": hotel_codes,
            "fields": "all",
        }

        response = self.transport.hotel_content(**params)
        hotel_contents = self._check_hotel_content_response_and_get_results(response)
        hotel_contents_map = {x["code"]: x for x in hotel_contents}

        return hotel_contents_map

    def _create_hotel_from_response(self, search, hotel_response):
        room_types = self._create_room_types(hotel_response)
        rate_plans = self._create_rate_plans(hotel_response)
        room_rates = self._create_room_rates(hotel_response)
        hotel_details = HotelDetails(name="", address=Address(), hotel_code=hotel_response["code"],)

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

    def _enrich_hotels(self, hotels: Union[List[AdapterHotel], AdapterHotel]):
        logger.info("Enrichment: Begin")
        if isinstance(hotels, AdapterHotel):
            hotels = [hotels]

        hotel_codes = list(x.hotel_id for x in hotels)
        logger.info(f"Enrichment: Looking up {len(hotel_codes)} hotels")
        hotelbeds_hotels = ProviderHotel.objects.filter(
            provider__name=self.get_provider_name(), provider_code__in=hotel_codes
        )
        hotel_details_map = {x.provider_code: x for x in hotelbeds_hotels}
        logger.info(f"Enrichment: Found {len(hotel_details_map)} stored hotels")

        logger.info(f"Enrichment: Looking up images for {len(hotel_codes)} hotels")
        hotel_images = ProviderImages.objects.filter(provider=self.provider, provider_code__in=hotel_codes)
        logger.info(f"Enrichment: Found {len(hotel_images)} stored images")

        hotel_images_by_id = defaultdict(list)
        for image in hotel_images:
            hotel_images_by_id[image.provider_code].append(image)

        for hotel in hotels:
            if hotel.hotel_id not in hotel_details_map:
                continue

            hotel_detail_model = hotel_details_map[hotel.hotel_id]
            photos = list(map(self._get_image, hotel_images_by_id.get(hotel.hotel_id) or []))
            hotel.hotel_details = self._create_hotel_details(hotel, hotel_detail_model, photos)

        logger.info("Enrichment: Complete")

    def search_by_id(self, search: AdapterHotelSearch) -> AdapterHotel:
        request = self._create_hotel_id_search(search)

        response = self.transport.hotels(**request)
        hotel_results = self._check_hotels_response_and_get_results(response)
        hotel = self._create_hotel_from_response(search, hotel_results[0])

        self._enrich_hotels(hotel)

        return hotel

    def search_by_id_batch(self, search: AdapterHotelBatchSearch) -> List[AdapterHotel]:
        request = self._create_hotel_id_batch_search(search)

        response = self.transport.hotels(**request)
        hotel_results = self._check_hotels_response_and_get_results(response)

        hotels = list(map(lambda result: self._create_hotel_from_response(search, result), hotel_results,))
        self._enrich_hotels(hotels)

        return hotels

    def details(self, *args) -> HotelDetails:
        pass

    def reviews(self, *args) -> HotelReviews:
        raise NotImplementedError()

    def recheck(self, room_rate: RoomRate) -> RoomRate:
        request = self._create_recheck_params(room_rate)

        response = self.transport.checkrates(**request)
        hotel_result = self._check_checkrates_response_and_get_results(response)

        room_type_code = hotel_result["rooms"][0]["code"]
        room_rate = hotel_result["rooms"][0]["rate"][0]

        return self._create_room_rate(room_type_code, room_rate, hotel_result["currency"])

    def booking(self, book_request: HotelBookingRequest) -> HotelReservation:
        request = self._create_booking_params(book_request)
        response = self.transport.booking(**request)

        results = self._check_booking_response_and_get_results(response)
        booking_locator = results["reference"]
        hotel_data = results["hotel"]

        checkin = datetime.strptime(hotel_data["checkIn"], "%Y-%m-%d").date()
        checkout = datetime.strptime(hotel_data["checkOut"], "%Y-%m-%d").date()

        booked_rate_data = hotel_data["rooms"][0]["rates"][0]
        booked_room_rate = self._create_room_rates(hotel_data)[0]

        cancellation_details = self._parse_cancellation_details(booked_rate_data, hotel_data["currency"])

        return HotelReservation(
            locator=Locator(id=booking_locator),
            hotel_locator=None,
            hotel_id=book_request.hotel_id,
            checkin=checkin,
            checkout=checkout,
            customer=book_request.customer,
            traveler=book_request.traveler,
            room_rate=booked_room_rate,
            cancellation_details=cancellation_details,
        )

    def cancel(self, cancel_request: AdapterCancelRequest) -> AdapterCancelResponse:
        lookup_request = {"language": cancel_request.language}
        lookup_response = self.transport.booking_detail(cancel_request.record_locator, **lookup_request)
        lookup_result = self._check_booking_response_and_get_results(lookup_response)

        if (
            "cancellation" not in lookup_result["modificationPolicies"]
            or not lookup_result["modificationPolicies"]["cancellation"]
        ):
            raise BookingException(BookingErrorCode.PROVIDER_CANCELLATION_FAILURE, "Could not cancel booking")

        request = {"cancellationFlag": "CANCELLATION", "language": cancel_request.language}
        cancel_response = self.transport.booking_cancel(cancel_request.record_locator, **request)
        cancel_result = self._check_booking_response_and_get_results(cancel_response)

        if cancel_result["status"] != "CANCELLED":
            logger.error(f"Could not cancel booking {cancel_request}: {cancel_response}")
            raise BookingException(BookingErrorCode.CANCELLATION_FAILURE, "Could not cancel booking")

        return AdapterCancelResponse(is_cancelled=True)

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
            occupancy = RoomOccupancy(adults=adults, children=children)
            room_type = RoomType(
                code=room["code"],
                name=room["name"],
                description=room["name"],
                amenities=[],
                photos=[],
                capacity=occupancy,
                bed_types=None,
            )

            room_types.append(room_type)

        return room_types

    def _create_rate_plans(self, hotel_response):
        """
        "rateKey": "20190615|20190616|W|1|297|DBT.ST|NRF-SUMMERHB|HB||1~2~0||N@A09243E85DB5477DA580C281A6DD9DBE1613",
        "rateClass": "NOR",
        "rateType": "BOOKABLE",
        "net": "137.62",
        "allotment": 96,
        "paymentType": "AT_WEB",
        "packaging": false,
        "boardCode": "HB",
        "boardName": "HALF BOARD",
        "cancellationPolicies": [
            {
                "amount": "68.81",
                "from": "2019-05-31T21:59:00.000Z"
            },
            {
                "amount": "137.62",
                "from": "2019-06-14T21:59:00.000Z"
            }
        ],
        """
        rate_plans = []
        for room in hotel_response["rooms"]:
            for rate in room["rates"]:
                cancellation_details = self._parse_cancellation_details(rate, hotel_response["currency"])
                most_lenient_cancellation_policy = self._cancellation_summary_from_details(cancellation_details)

                rate_plan = RatePlan(
                    code=rate["rateKey"],
                    name="",
                    description="",
                    amenities=[],
                    cancellation_policy=most_lenient_cancellation_policy,
                )
                rate_plans.append(rate_plan)

        return rate_plans

    @staticmethod
    def _parse_cancellation_details(rate, currency) -> List[CancellationDetails]:
        total_rate = rate["net"]
        cancellation_detail_lst = []
        if "cancellationPolicies" not in rate or len(rate["cancellationPolicies"]) == 0:
            return [
                CancellationDetails(
                    cancellation_type=CancellationSummary.UNKNOWN_CANCELLATION_POLICY,
                    description="Cancellation policy unspecified",
                    begin_date=datetime.now() - relativedelta(years=1),
                    end_date=datetime.now() + relativedelta(years=5),
                    penalty_amount=total_rate,
                    penalty_currency=currency,
                )
            ]

        for cancellation_detail_response in rate["cancellationPolicies"]:
            total_penalty = cancellation_detail_response["amount"]
            from_date = datetime.fromisoformat(cancellation_detail_response["from"])
            # end_date=datetime.now() + relativedelta(years=5)

            cancellation_type = CancellationSummary.NON_REFUNDABLE
            current_time = datetime.now(tz=pytz.timezone("US/Pacific"))

            if current_time >= from_date:
                if total_penalty == rate["net"]:
                    cancellation_type = CancellationSummary.FREE_CANCELLATION
                elif Decimal(total_penalty) < Decimal(rate["net"]):
                    cancellation_type = CancellationSummary.PARTIAL_REFUND

            cancellation_detail = CancellationDetails(
                cancellation_type=cancellation_type,
                description="",
                begin_date=from_date,
                end_date=None,
                penalty_amount=total_penalty,
                penalty_currency=currency,
            )

            cancellation_detail_lst.append(cancellation_detail)

        return cancellation_detail_lst

    @staticmethod
    def _cancellation_summary_from_details(cancellation_details: List[CancellationDetails],) -> CancellationPolicy:
        sort_order = {
            CancellationSummary.FREE_CANCELLATION: 0,
            CancellationSummary.PARTIAL_REFUND: 1,
            CancellationSummary.NON_REFUNDABLE: 2,
        }

        most_lenient_policy = sorted(cancellation_details, key=lambda x: sort_order.get(x.cancellation_type))[0]

        return CancellationPolicy(
            summary=most_lenient_policy.cancellation_type,
            cancellation_deadline=most_lenient_policy.end_date,
            unstructured_policy=most_lenient_policy.description,
        )

    def _create_room_rates(self, hotel_response):
        room_rates = []
        for room in hotel_response["rooms"]:
            for rate in room["rates"]:
                room_rates.append(self._create_room_rate(room["code"], rate, hotel_response["currency"]))

        return room_rates

    def _create_room_rate(self, room_type_code: str, rate: Dict[Any, Any], currency="USD"):
        net_amount = rate["net"]
        if net_amount is None:
            net_amount = Decimal("0.0")

        total_base_rate = Money(amount=net_amount, currency=currency)
        total_taxes = 0
        if "taxes" in rate:
            total_taxes = sum(Decimal(x["amount"]) for x in rate["taxes"]["taxes"] if x["amount"] is not None)

        total_tax_rate = Money(amount=total_taxes, currency=currency)
        total_amount = total_base_rate.amount + total_tax_rate.amount
        total_rate = Money(amount=total_amount, currency=currency)

        occupancy = RoomOccupancy(adults=rate["adults"], children=rate["children"], num_rooms=rate["rooms"])

        rate_type = "BOOKABLE"
        if "rateType" in rate:
            rate_type = self._get_rate_type(rate["rateType"])

        code = room_type_code
        if "rateKey" in rate:
            code = rate["rateKey"]

        return RoomRate(
            code=code,
            rate_plan_code=code,
            room_type_code=room_type_code,
            rate_type=rate_type,
            total_base_rate=total_base_rate,
            total_tax_rate=total_tax_rate,
            total=total_rate,
            maximum_allowed_occupancy=occupancy,
        )

    def _check_hotels_response_and_get_results(self, response):
        results = self._check_operation_response_and_get_results(response, "hotels")
        return results["hotels"]

    def _check_hotel_content_response_and_get_results(self, response):
        results = self._check_operation_response_and_get_results(response, "hotels")
        return results

    def _check_checkrates_response_and_get_results(self, response):
        results = self._check_operation_response_and_get_results(response, "hotels")
        return results

    @staticmethod
    def _check_operation_response_and_get_results(response, operation):
        if response is None:
            raise AvailabilityException(
                error_type=AvailabilityErrorCode.PROVIDER_ERROR, detail="Could not retrieve response",
            )
        if "error" in response:
            error_message = response["error"]
            if "message" in error_message:
                error_message = error_message["message"]
            logger.error("Error in Hotelbeds Message: " + error_message)
            raise AvailabilityException(error_type=AvailabilityErrorCode.PROVIDER_ERROR, detail=error_message)

        return response[operation]

    def _create_booking_params(self, book_request: HotelBookingRequest):
        return {
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

    def _check_booking_response_and_get_results(self, response):
        if response is None:
            raise BookingException(
                error_type=AvailabilityErrorCode.PROVIDER_ERROR, detail="Could not retrieve response",
            )
        if "error" in response:
            error_message = response["error"]
            if "message" in error_message:
                error_message = error_message["message"]
            logger.error("Error in Hotelbeds Message: " + error_message)
            raise BookingException(error_type=AvailabilityErrorCode.PROVIDER_ERROR, detail=error_message)

        return response["booking"]

    @staticmethod
    def _get_rate_type(rate_type: str):
        if rate_type == "RECHECK":
            return "RECHECK"

        return "BOOKABLE"

    @staticmethod
    def _get_image(provider_image: ProviderImages):
        return Image(url=provider_image.image_url, type=ImageType.UNKNOWN, display_order=provider_image.display_order,)

    @staticmethod
    def _create_hotel_details(hotel, hotel_detail_model: ProviderHotel, photos):
        return HotelDetails(
            name=hotel_detail_model.hotel_name,
            address=hotel_detail_model.get_address(),
            hotel_code=hotel.hotel_id,
            checkin_time=None,
            checkout_time=None,
            photos=photos,
            amenities=get_simplenight_amenity_mappings(hotel_detail_model.amenities),
            thumbnail_url=hotel_detail_model.thumbnail_url,
            star_rating=hotel_detail_model.star_rating,
            property_description=hotel_detail_model.property_description,
        )

    def _create_recheck_params(self, room_rate: RoomRate):
        return {"rooms": [{"rateKey": room_rate.code}]}

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
