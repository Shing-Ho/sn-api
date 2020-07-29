import uuid
from decimal import Decimal
from typing import List

from api.common.models import Money
from api.hotel.adapters.translate.google.models import (
    GoogleHotelApiResponse,
    GoogleHotelSearchRequest,
    GoogleRoomType,
    DisplayString,
    BasicAmenities,
    GoogleImage,
    RoomCapacity,
    GoogleRatePlan,
    GuaranteeType,
    GoogleCancellationPolicy,
    GoogleRoomRate,
    RoomRateLineItem,
    LineItemType, GoogleHotelDetails, CancellationSummary,
)
from api.hotel.hotel_model import Hotel, SimplenightAmenities, Image


def translate_hotel_response(search_request: GoogleHotelSearchRequest, hotel: Hotel) -> GoogleHotelApiResponse:
    room_types = _get_room_types(hotel, search_request.language)
    rate_plans = _get_rate_plans(hotel, search_request.language)

    room_type_code = room_types[0].code
    rate_plan_code = rate_plans[0].code

    return GoogleHotelApiResponse(
        api_version=1,
        transaction_id=search_request.transaction_id,
        hotel_id=search_request.hotel_id,
        start_date=search_request.start_date,
        end_date=search_request.end_date,
        party=search_request.party,
        room_types=room_types,
        rate_plans=rate_plans,
        room_rates=_get_room_rates(hotel, room_type_code, rate_plan_code),
        hotel_details=_get_hotel_details(hotel),
    )


# TODO: Actually implement rate plan logic
def _get_rate_plans(hotel: Hotel, language: str) -> List[GoogleRatePlan]:
    rate_plan = GoogleRatePlan(
        code="foo",
        name=DisplayString("Rate Plan", language),
        description=DisplayString("The Description", language),
        basic_amenities=_get_basic_amenity_mapping(hotel.hotel_details.amenities),
        guarantee_type=GuaranteeType.PAYMENT_CARD,
        cancellation_policy=_get_google_cancellation_policy(hotel, language),
    )

    return [rate_plan]


# TODO: Integrate photos into room types
def _get_room_types(hotel: Hotel, language="en") -> List[GoogleRoomType]:
    room_types = []
    for room_type in hotel.room_types:
        room_types.append(
            GoogleRoomType(
                code=room_type.code,
                name=DisplayString(room_type.name, language),
                description=DisplayString(room_type.description, language),
                basic_amenities=BasicAmenities(False, False, False),
                photos=[],
                capacity=RoomCapacity(room_type.capacity.adults, room_type.capacity.children),
            )
        )

    return room_types


def _get_basic_amenity_mapping(amenities: List[SimplenightAmenities]) -> BasicAmenities:
    has_free_parking = SimplenightAmenities.PARKING in amenities
    has_free_breakfast = SimplenightAmenities.BREAKFAST in amenities
    has_free_wifi = SimplenightAmenities.WIFI in amenities

    return BasicAmenities(free_breakfast=has_free_breakfast, free_wifi=has_free_wifi, free_parking=has_free_parking)


# TODO: Add descriptive text for images
def _get_photos(images: List[Image], language: str) -> List[GoogleImage]:
    return list(GoogleImage(image.url, DisplayString(image.type.value, language)) for image in images)


# TODO: Actually implement cancellation policies
def _get_google_cancellation_policy(hotel: Hotel, language):
    return GoogleCancellationPolicy(
        summary=CancellationSummary.NON_REFUNDABLE,
        cancellation_deadline="10 days before",
        unstructured_policy=DisplayString("The cancellation details", language),
    )


def _get_room_rates(hotel: Hotel, room_type_code, rate_plan_code) -> List[GoogleRoomRate]:
    room_rates = []
    room_type = hotel.room_types[0]
    for room_rate in room_type.rates:
        room_rates.append(
            GoogleRoomRate(
                code=str(uuid.uuid4()),
                room_type_code=room_type_code,
                rate_plan_code=rate_plan_code,
                maximum_allowed_occupancy=RoomCapacity(room_type.capacity.adults, room_type.capacity.children),
                total_price_at_booking=room_type.rates[0].total,
                total_price_at_checkout=Money(Decimal("0.00"), room_type.rates[0].total.currency),
                line_items=[
                    RoomRateLineItem(room_rate.total_base_rate, LineItemType.BASE_RATE, False),
                    RoomRateLineItem(room_rate.total_tax_rate, LineItemType.UNKNOWN_TAXES, False),
                ],
            )
        )

    return room_rates


def _get_hotel_details(hotel: Hotel) -> GoogleHotelDetails:
    return GoogleHotelDetails(
        name=hotel.hotel_details.name,
        address=hotel.hotel_details.address,
        geolocation=hotel.hotel_details.geolocation,
        phone_number=hotel.hotel_details.phone_number,
        email=hotel.hotel_details.email,
    )
