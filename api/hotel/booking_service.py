from datetime import datetime
from typing import Union

from api import logger
from api.hotel.models.booking_model import HotelBookingRequest, HotelBookingResponse, Customer, Status
from api.common.models import RoomRate
from api.hotel import price_verification_service, hotel_cache_service
from api.hotel.adapters import adapter_service
from api.hotel.models.hotel_api_model import SimplenightRoomType
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
        reservation = adapter.booking(book_request)
        reservation.room_rate = simplenight_rate  # TODO: Don't create Reservation in Adapter

        if not reservation or not reservation.locator:
            logger.error(f"Could not book request: {book_request}")
            raise AppException("Error during booking")

        booking = persist_reservation(book_request, provider_rate_cache_payload, reservation)

        return HotelBookingResponse(
            api_version=1,
            transaction_id=book_request.transaction_id,
            booking_id=str(booking.booking_id),
            status=Status(success=True, message="success"),
            reservation=reservation
        )

    except BookingException as e:
        raise e
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


def persist_reservation(book_request, provider_rate_cache_payload, reservation):
    traveler = _persist_traveler(reservation.customer)
    booking = _persist_booking_record(book_request, traveler)
    _persist_hotel(book_request, provider_rate_cache_payload, booking, reservation)

    return booking


def _persist_hotel(book_request, provider_rate_cache_payload, booking, reservation):
    # Takes the original room rates as a parameter
    # Persists both the provider rate (on book_request) and the original rates
    simplenight_rate = reservation.room_rate
    provider_rate = provider_rate_cache_payload.provider_rate
    hotel_booking = models.HotelBooking(
        booking=booking,
        created_date=datetime.now(),
        hotel_name="Hotel Name",
        provider_name=provider_rate_cache_payload.provider,
        hotel_code=book_request.hotel_id,
        record_locator=reservation.locator.id,
        total_price=simplenight_rate.total.amount,
        currency=simplenight_rate.total.currency,
        provider_total=provider_rate.total.amount,
        provider_currency=provider_rate.total.currency,
    )

    hotel_booking.save()

    cancellation_details = reservation.cancellation_details
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


def _persist_booking_record(booking_request, traveler):
    booking = models.Booking(
        booking_status=BookingStatus.BOOKED.value,
        transaction_id=booking_request.transaction_id,
        booking_date=datetime.now(),
        lead_traveler=traveler,
    )

    booking.save()
    return booking


def _persist_traveler(customer: Customer):
    traveler = Traveler(
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone_number=customer.phone_number,
        email_address=customer.email,
        country=customer.country[:2],
    )

    traveler.save()
    return traveler
