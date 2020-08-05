from datetime import datetime
from typing import List

from api import logger
from api.booking.booking_model import HotelBookingRequest, HotelBookingResponse
from api.common.models import RoomRate, Money
from api.hotel.adapters import adapter_service
from api.models import models
from api.models.models import BookingStatus, Traveler
from api.payments import payment_service
from common.exceptions import AppException


def book(book_request: HotelBookingRequest) -> HotelBookingResponse:
    adapter = adapter_service.get_adapter(book_request.crs)
    total_payment_amount = _get_payment_amount(book_request)
    auth_response = payment_service.authorize_payment(
        amount=total_payment_amount,
        payment=book_request.payment,
        description=f"Simplenight Hotel Booking {book_request.hotel_id}",
    )

    if not auth_response:
        logger.error(f"Could not authorize payment for booking: {book_request}")
        raise AppException("Error authorizing payment")

    response = adapter.booking(book_request)

    if not response or not response.reservation.locator:
        logger.error(f"Could not book request: {book_request}")
        raise AppException("Error during booking")

    persist_reservation(book_request, response)

    return response


def _get_payment_amount(book_request: HotelBookingRequest):
    # TODO: Validate these payment amounts better
    # TODO: Validate currency
    total_payment_amount = sum(x.total.amount for x in book_request.room_rates)
    return Money(total_payment_amount, book_request.room_rates[0].total.currency)


def _price_verification(rooms: List[RoomRate]):
    pass


def persist_reservation(book_request, response):
    traveler = _persist_traveler(response)
    booking = _persist_booking_record(response, traveler)
    _persist_hotel(book_request, booking, response)

    return booking


def _persist_hotel(book_request, booking, response):
    for rate in response.reservation.room_rates:
        hotel_booking = models.HotelBooking(
            booking=booking,
            created_date=datetime.now(),
            hotel_name="Hotel Name",
            crs_name=book_request.crs,
            hotel_code=book_request.hotel_id,
            record_locator=response.reservation.locator.id,
            total_price=rate.total.amount,
            currency=rate.total.currency,
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
