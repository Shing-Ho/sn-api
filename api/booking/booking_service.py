from datetime import datetime
from typing import List

from api import logger
from api.booking.booking_model import HotelBookingRequest, HotelBookingResponse
from api.common import cache_storage
from api.common.models import RoomRate, Money
from api.hotel.adapters import adapter_service
from api.models import models
from api.models.models import BookingStatus, Traveler
from api.payments import payment_service
from common.exceptions import AppException


def book(book_request: HotelBookingRequest) -> HotelBookingResponse:
    adapter = adapter_service.get_adapter(book_request.provider)
    total_payment_amount = _get_payment_amount(book_request)
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
    room_rates = book_request.room_rates
    provider_rates = list(map(_get_provider_rate, book_request.room_rates))
    book_request.room_rates = provider_rates
    response = adapter.booking(book_request)

    if not response or not response.reservation.locator:
        logger.error(f"Could not book request: {book_request}")
        raise AppException("Error during booking")

    persist_reservation(book_request, room_rates, response)

    return response


def _get_payment_amount(book_request: HotelBookingRequest):
    # TODO: Validate these payment amounts better
    # TODO: Validate currency
    total_payment_amount = sum(x.total.amount for x in book_request.room_rates)
    return Money(total_payment_amount, book_request.room_rates[0].total.currency)


def _price_verification(rooms: List[RoomRate]):
    pass


def persist_reservation(book_request, room_rates, response):
    traveler = _persist_traveler(response)
    booking = _persist_booking_record(response, traveler)
    _persist_hotel(book_request, room_rates, booking, response)

    return booking


def _persist_hotel(book_request, room_rates, booking, response):
    # Takes the original room rates as a parameter
    # Persists both the provider rate (on book_request) and the original rates
    for provider_rate, rate in zip(response.reservation.room_rates, room_rates):
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
        country=response.reservation.customer.country,
    )

    traveler.save()
    return traveler


def _get_provider_rate(room_rate: RoomRate) -> RoomRate:
    provider_rate = cache_storage.get(room_rate.code)
    if not provider_rate:
        raise RuntimeError(f"Could not find Provider Rate for Rate Key {room_rate.code}")

    return provider_rate
