import uuid
from decimal import Decimal
from typing import List

from api.booking.booking_model import (
    HotelBookingRequest,
    Traveler,
    Payment,
    PaymentCardParameters,
    HotelBookingResponse,
)
from api.common.models import Money, RoomOccupancy, RoomRate, RateType
from api.hotel.hotel_model import Hotel, SimplenightAmenities, Image, HotelSpecificSearch
from api.hotel.translate.google_models import (
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
    GoogleHotelDetails,
    CancellationSummary,
    GoogleBookingSubmitRequest,
    GoogleTraveler,
    GoogleBookingResponse,
    GoogleStatus,
    GoogleReservation,
    RoomParty,
)
from api.tests import to_money


def translate_hotel_specific_search(google_search_request: GoogleHotelSearchRequest) -> HotelSpecificSearch:
    return HotelSpecificSearch(
        hotel_id=google_search_request.hotel_id,
        start_date=google_search_request.start_date,
        end_date=google_search_request.end_date,
        occupancy=RoomOccupancy(
            adults=google_search_request.party.adults, children=len(google_search_request.party.children)
        ),
        daily_rates=False,
    )


def translate_booking_request(google_booking_request: GoogleBookingSubmitRequest) -> HotelBookingRequest:
    google_room_rate = google_booking_request.room_rate

    total_price = Decimal()
    if google_room_rate.total_price_at_checkout:
        total_price += google_room_rate.total_price_at_checkout.amount

    if google_room_rate.total_price_at_booking:
        total_price += google_room_rate.total_price_at_booking.amount

    room_rate = RoomRate(
        rate_key=google_booking_request.room_rate.code,
        rate_type=RateType.BOOKABLE,
        description="",
        additional_detail=[],
        total_base_rate=Money(total_price, "USD"),
        total_tax_rate=to_money("0"),
        total=Money(total_price, "USD"),
    )

    google_payment = google_booking_request.payment
    payment = Payment(
        billing_address=google_payment.billing_address,
        payment_card_parameters=PaymentCardParameters(
            card_type=google_payment.payment_card_parameters.card_type,
            card_number=google_payment.payment_card_parameters.card_number,
            cardholder_name=google_payment.payment_card_parameters.cardholder_name,
            expiration_month=google_payment.payment_card_parameters.expiration_month,
            expiration_year=google_payment.payment_card_parameters.expiration_year,
            cvv=google_payment.payment_card_parameters.cvc,
        ),
        payment_method=google_payment.type,
        payment_token=google_payment.payment_token,
    )

    return HotelBookingRequest(
        api_version=google_booking_request.api_version,
        transaction_id=google_booking_request.transaction_id,
        hotel_id=google_booking_request.hotel_id,
        checkin=google_booking_request.start_date,
        checkout=google_booking_request.end_date,
        language=google_booking_request.language,
        customer=google_booking_request.customer,
        traveler=Traveler(
            first_name=google_booking_request.traveler.first_name,
            last_name=google_booking_request.traveler.last_name,
            occupancy=RoomOccupancy(
                adults=google_booking_request.traveler.occupancy.adults,
                children=len(google_booking_request.traveler.occupancy.children),
            ),
        ),
        room_rates=[room_rate],
        payment=payment,
        tracking=google_booking_request.tracking.campaign_id,
        ip_address=google_booking_request.ip_address,
    )


def translate_booking_response(
    booking_request: GoogleBookingSubmitRequest, booking_response: HotelBookingResponse
) -> GoogleBookingResponse:
    status = GoogleStatus.FAILURE
    if booking_response.status.success:
        status = GoogleStatus.SUCCESS

    return GoogleBookingResponse(
        api_version=booking_response.api_version,
        transaction_id=booking_response.transaction_id,
        status=status,
        reservation=GoogleReservation(
            locator=booking_response.reservation.locator,
            hotel_locators=[booking_response.reservation.hotel_locator],
            hotel_id=booking_response.reservation.hotel_id,
            start_date=booking_response.reservation.checkin,
            end_date=booking_response.reservation.checkout,
            customer=booking_response.reservation.customer,
            traveler=GoogleTraveler(
                first_name=booking_response.reservation.traveler.first_name,
                last_name=booking_response.reservation.traveler.last_name,
                occupancy=RoomParty(
                    adults=booking_response.reservation.traveler.occupancy.adults,
                    children=booking_request.traveler.occupancy.children,
                ),
            ),
            room_rate=booking_request.room_rate,
        ),
    )


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
        cancellation_policy=_get_google_cancellation_policy(language),
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
def _get_google_cancellation_policy(language):
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
                line_items=[]
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
