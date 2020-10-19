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
from api.hotel.converter.google_models import (
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
from api.hotel.hotel_api_model import SimplenightAmenities, Image, HotelSpecificSearch, Hotel, CancellationPolicy


def convert_hotel_specific_search(google_search_request: GoogleHotelSearchRequest) -> HotelSpecificSearch:
    return HotelSpecificSearch(
        hotel_id=google_search_request.hotel_id,
        start_date=google_search_request.start_date,
        end_date=google_search_request.end_date,
        occupancy=RoomOccupancy(
            adults=google_search_request.party.adults, children=len(google_search_request.party.children)
        ),
        daily_rates=False,
    )


def convert_booking_request(google_booking_request: GoogleBookingSubmitRequest) -> HotelBookingRequest:
    google_room_rate = google_booking_request.room_rate

    total_price = Decimal()
    if google_room_rate.total_price_at_checkout:
        total_price += google_room_rate.total_price_at_checkout.amount

    if google_room_rate.total_price_at_booking:
        total_price += google_room_rate.total_price_at_booking.amount

    google_room_occupancy = google_booking_request.room_rate.maximum_allowed_occupancy
    room_occupancy = RoomOccupancy(adults=google_room_occupancy.adults, children=google_room_occupancy.children)

    room_rate = RoomRate(
        code=google_booking_request.room_rate.code,
        rate_plan_code=google_booking_request.room_rate.rate_plan_code,
        room_type_code=google_booking_request.room_rate.room_type_code,
        maximum_allowed_occupancy=room_occupancy,
        rate_type=RateType.BOOKABLE,
        total_base_rate=Money(amount=total_price, currency="USD"),
        total_tax_rate=Money(amount=Decimal("0"), currency="USD"),
        total=Money(amount=total_price, currency="USD"),
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
        room_code=room_rate.code,
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
        payment=payment,
    )


def convert_booking_response(
    booking_request: GoogleBookingSubmitRequest, booking_response: HotelBookingResponse
) -> GoogleBookingResponse:
    status = GoogleStatus.FAILURE
    if booking_response.status.success:
        status = GoogleStatus.SUCCESS

    google_booking_response = GoogleBookingResponse(
        api_version=booking_response.api_version,
        transaction_id=booking_response.transaction_id,
        status=status,
        reservation=GoogleReservation(
            locator=booking_response.reservation.locator,
            hotel_locators=[],
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

    hotel_locators = booking_response.reservation.hotel_locator
    if hotel_locators:
        google_booking_response.reservation.hotel_locators.extend(hotel_locators)

    return google_booking_response


def convert_hotel_response(search_request: GoogleHotelSearchRequest, hotel: Hotel) -> GoogleHotelApiResponse:
    room_types = _get_room_types(hotel, search_request.language)
    rate_plans = _get_rate_plans(hotel)

    return GoogleHotelApiResponse(
        api_version=1,
        transaction_id=search_request.transaction_id,
        hotel_id=hotel.hotel_id,
        start_date=hotel.start_date,
        end_date=hotel.end_date,
        party=search_request.party,
        room_types=room_types,
        rate_plans=rate_plans,
        room_rates=_get_room_rates(hotel),
        hotel_details=_get_hotel_details(hotel),
    )


def _get_rate_plans(hotel: Hotel) -> List[GoogleRatePlan]:
    rate_plans = []
    for rate_plan in hotel.rate_plans:
        rate_plans.append(
            GoogleRatePlan(
                code=rate_plan.code,
                name=DisplayString(text=rate_plan.name, language="en"),
                description=DisplayString(text=rate_plan.description, language="en"),
                basic_amenities=_get_basic_amenity_mapping(rate_plan.amenities),
                guarantee_type=GuaranteeType.PAYMENT_CARD,
                cancellation_policy=_get_google_cancellation_policy(rate_plan.cancellation_policy, language="en"),
            )
        )

    return rate_plans


def _get_room_types(hotel: Hotel, language="en") -> List[GoogleRoomType]:
    room_types = []
    for room_type in hotel.room_types:
        room_types.append(
            GoogleRoomType(
                code=room_type.code,
                name=DisplayString(text=room_type.name, language=language),
                description=DisplayString(text=room_type.description, language=language),
                basic_amenities=BasicAmenities(free_breakfast=False, free_wifi=False, free_parking=False),
                photos=list(map(_get_image_mapping, room_type.photos)),
                capacity=RoomCapacity(adults=room_type.capacity.adults, children=room_type.capacity.children),
            )
        )

    return room_types


def _get_image_mapping(photo: Image) -> GoogleImage:
    return GoogleImage(url=photo.url, description=DisplayString(text="", language="en"))


def _get_basic_amenity_mapping(amenities: List[SimplenightAmenities]) -> BasicAmenities:
    has_free_parking = SimplenightAmenities.PARKING in amenities
    has_free_breakfast = SimplenightAmenities.BREAKFAST in amenities
    has_free_wifi = SimplenightAmenities.WIFI in amenities

    return BasicAmenities(free_breakfast=has_free_breakfast, free_wifi=has_free_wifi, free_parking=has_free_parking)


# TODO: Add descriptive text for images
def _get_photos(images: List[Image], language: str) -> List[GoogleImage]:
    return list(
        GoogleImage(url=image.url, description=DisplayString(text=image.type.value, language=language))
        for image in images
    )


# TODO: Actually implement cancellation policies
def _get_google_cancellation_policy(cancellation_policy: CancellationPolicy, language):
    return GoogleCancellationPolicy(
        summary=CancellationSummary.NON_REFUNDABLE,
        cancellation_deadline="10 days before",
        unstructured_policy=DisplayString(text="The cancellation details", language=language),
    )


def _get_room_rates(hotel: Hotel) -> List[GoogleRoomRate]:
    room_rates = []
    for room_rate in hotel.room_rates:
        capacity = room_rate.maximum_allowed_occupancy
        room_rates.append(
            GoogleRoomRate(
                code=room_rate.code,
                room_type_code=room_rate.room_type_code,
                rate_plan_code=room_rate.rate_plan_code,
                maximum_allowed_occupancy=RoomCapacity(adults=capacity.adults, children=capacity.children),
                total_price_at_booking=room_rate.total,
                total_price_at_checkout=Money(amount=Decimal("0.00"), currency=room_rate.total.currency),
                line_items=[],
                partner_data=[],
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
