from datetime import datetime
from typing import Union

from api import logger
from api.booking.booking_model import HotelBookingRequest, HotelBookingResponse
from api.common.models import RoomRate
from api.hotel import price_verification_service, hotel_cache_service
from api.hotel.adapters import adapter_service
from api.hotel.hotel_model import SimplenightRoomType
from api.models import models
from api.models.models import BookingStatus, Traveler
from api.payments import payment_service
from api.view.exceptions import BookingException, BookingErrorCode
from common.exceptions import AppException


def book(book_request: HotelBookingRequest) -> HotelBookingResponse:
    try:
        provider_rate_cache_payload = hotel_cache_service.get_cached_room_data(book_request.room_code)
        provider = provider_rate_cache_payload.provider
        simplenight_rate = provider_rate_cache_payload.simplenight_rate
        adapter = adapter_service.get_adapter(provider)

        total_payment_amount = simplenight_rate.total
        auth_response = payment_service.authorize_payment(
            amount=total_payment_amount,
            payment=book_request.payment,
            description=f"Simplenight Hotel Booking {book_request.hotel_id}",
        )

        if not auth_response:
            logger.error(f"Could not authorize payment for booking: {book_request}")
            raise AppException("Error authorizing payment")

        # Save Simplenight Internal Room Rates
        # Lookup Provider Rates in Cache
        provider_rate = provider_rate_cache_payload.provider_rate
        book_request.room_code = provider_rate.code

        # Reset room rates with verified rates.  If prices mismatch, error will raise
        verified_rates = _price_verification(provider=provider, rate=provider_rate)
        book_request.room_code = verified_rates.code
        response = adapter.booking(book_request)
        response.reservation.room_rate = simplenight_rate  # TODO: Don't create Reservation in Adapter

        if not response or not response.reservation.locator:
            logger.error(f"Could not book request: {book_request}")
            raise AppException("Error during booking")

        persist_reservation(book_request, simplenight_rate, response)

        return response

    except Exception as e:
        raise BookingException(BookingErrorCode.UNHANDLED_ERROR, str(e))


def _price_verification(provider: str, rate: Union[SimplenightRoomType, RoomRate]):
    price_verification = price_verification_service.recheck(provider=provider, room_rate=rate)

    if not price_verification.is_allowed_change:
        old_price = rate.total.amount
        new_price = price_verification.verified_room_rate.total.amount
        error_msg = f"Price Verification Failed: Old={old_price}, New={new_price}"
        raise BookingException(BookingErrorCode.PRICE_VERIFICATION, error_msg)

    return price_verification.verified_room_rate


def persist_reservation(book_request, room_rate, response):
    traveler = _persist_traveler(response)
    booking = _persist_booking_record(response, traveler)
    _persist_hotel(book_request, room_rate, booking, response)

    return booking


def _persist_hotel(book_request, room_rate, booking, response):
    # Takes the original room rates as a parameter
    # Persists both the provider rate (on book_request) and the original rates
    provider_rate, rate = response.reservation.room_rate, room_rate
    hotel_booking = models.HotelBooking(
        booking=booking,
        created_date=datetime.now(),
        hotel_name="Hotel Name",
        provider_name=book_request.provider,
        hotel_code=book_request.hotel_id,
        record_locator=response.reservation.locator.id,
        total_price=rate.total.amount,
        currency=rate.total.currency,
        provider_total=provider_rate.total.amount,
        provider_currency=provider_rate.total.currency,
    )

    hotel_booking.save()

    cancellation_details = response.reservation.cancellation_details
    cancellation_policy_models = []
    for cancellation_policy in cancellation_details:
        cancellation_policy_models.append(models.HotelCancellationPolicy(
            hotel_booking=hotel_booking,
            cancellation_type=cancellation_policy.cancellation_type.value,
            description=cancellation_policy.description,
            begin_date=cancellation_policy.begin_date,
            end_date=cancellation_policy.end_date,
            penalty_amount=cancellation_policy.penalty_amount,
            penalty_currency=cancellation_policy.penalty_currency
        ))

    if len(cancellation_policy_models) > 0:
        logger.info(f"Persisting cancellation policies for booking: {hotel_booking.hotel_booking_id}")
        models.HotelCancellationPolicy.objects.bulk_create(cancellation_policy_models)


def _persist_booking_record(response, traveler):
    booking = models.Booking(
        booking_status=BookingStatus.BOOKED.value,
        transaction_id=response.transaction_id,
        booking_date=datetime.now(),
        lead_traveler=traveler,
    )

    booking.save()
    return booking


def _persist_traveler(response):
    traveler = Traveler(
        first_name=response.reservation.customer.first_name,
        last_name=response.reservation.customer.last_name,
        phone_number=response.reservation.customer.phone_number,
        email_address=response.reservation.customer.email,
        country=response.reservation.customer.country[:2],
    )

    traveler.save()
    return traveler
