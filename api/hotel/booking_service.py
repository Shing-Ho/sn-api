from datetime import datetime
from typing import Union

from api import logger
from api.hotel.models.hotel_common_models import Money, RoomRate
from api.hotel import price_verification_service, hotel_cache_service
from api.hotel.adapters import adapter_service
from api.hotel.models.adapter_models import AdapterCancelRequest
from api.hotel.models.booking_model import HotelBookingRequest, HotelBookingResponse, Customer, Status
from api.hotel.models.hotel_api_model import (
    SimplenightRoomType,
    CancelRequest,
    CancelResponse,
    CancellationDetails,
    CancellationSummary,
    HotelItineraryItem,
    CancelConfirmResponse,
)
from api.models import models
from api.models.models import (
    BookingStatus,
    Traveler,
    Provider,
    HotelBooking,
    Booking,
    HotelCancellationPolicy,
    ProviderHotel,
    PaymentTransaction,
    RecordLocator,
)
from api.payments import payment_service
from api.view.exceptions import BookingException, BookingErrorCode
from common.exceptions import AppException


def book(book_request: HotelBookingRequest) -> HotelBookingResponse:
    try:
        provider_rate_cache_payload = hotel_cache_service.get_cached_room_data(book_request.room_code)
        provider = provider_rate_cache_payload.provider
        simplenight_rate = provider_rate_cache_payload.simplenight_rate
        adapter = adapter_service.get_adapter(provider)

        traveler = _persist_traveler(book_request.customer)
        booking = _persist_booking_record(book_request, traveler)
        simplenight_record_locator = RecordLocator.generate_record_locator(booking)

        logger.info(f"Saved booking {booking.booking_id}")

        total_payment_amount = simplenight_rate.total
        auth_response = payment_service.authorize_payment(
            amount=total_payment_amount,
            payment=book_request.payment,
            description=f"Simplenight Hotel Booking {book_request.hotel_id}",
        )

        if not auth_response:
            logger.error(f"Could not authorize payment for booking: {book_request}")
            raise AppException("Error authorizing payment")
        elif auth_response.charge_id is not None:
            logger.info(f"Successfully charged Charge ID {auth_response.charge_id}")
            auth_response.booking = booking
            auth_response.save()

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

        _set_booked_status(booking)
        _persist_hotel(book_request, provider_rate_cache_payload, booking, reservation)

        return HotelBookingResponse(
            api_version=1,
            transaction_id=book_request.transaction_id,
            booking_id=simplenight_record_locator,
            status=Status(success=True, message="success"),
            reservation=reservation,
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


def _persist_hotel(book_request, provider_rate_cache_payload, booking, reservation):
    # Takes the original room rates as a parameter
    # Persists both the provider rate (on book_request) and the original rates
    simplenight_rate = reservation.room_rate
    provider_rate = provider_rate_cache_payload.provider_rate
    adapter_hotel = provider_rate_cache_payload.adapter_hotel
    provider = Provider.objects.get(name=provider_rate_cache_payload.provider)
    hotel_booking = models.HotelBooking(
        provider=provider,
        booking=booking,
        created_date=datetime.now(),
        hotel_name=adapter_hotel.hotel_details.name,
        simplenight_hotel_id=book_request.hotel_id,  # TODO: Don't use hotel id from request
        provider_hotel_id=provider_rate_cache_payload.hotel_id,
        record_locator=reservation.locator.id,
        total_price=simplenight_rate.total.amount,
        currency=simplenight_rate.total.currency,
        provider_total=provider_rate.total.amount,
        provider_currency=provider_rate.total.currency,
        checkin=adapter_hotel.start_date,
        checkout=adapter_hotel.end_date,
    )

    hotel_booking.save()

    cancellation_details = reservation.cancellation_details
    cancellation_policy_models = []
    for cancellation_policy in cancellation_details:
        cancellation_policy_models.append(
            models.HotelCancellationPolicy(
                hotel_booking=hotel_booking,
                cancellation_type=cancellation_policy.cancellation_type.value,
                description=cancellation_policy.description,
                begin_date=cancellation_policy.begin_date,
                end_date=cancellation_policy.end_date,
                penalty_amount=cancellation_policy.penalty_amount,
                penalty_currency=cancellation_policy.penalty_currency,
            )
        )

    if len(cancellation_policy_models) > 0:
        logger.info(f"Persisting cancellation policies for hotel booking: {hotel_booking.hotel_booking_id}")
        models.HotelCancellationPolicy.objects.bulk_create(cancellation_policy_models)


def cancel_lookup(cancel_request: CancelRequest) -> CancelResponse:
    simplenight_locator = cancel_request.booking_id
    last_name = cancel_request.last_name

    try:
        booking = _find_booking_with_booking_id_and_lastname(simplenight_locator, last_name)
        hotel_booking = HotelBooking.objects.get(booking_id=booking.booking_id)
        policy = _find_active_cancellation_policy(booking.booking_id)
        itinerary = _create_itinerary(hotel_booking)
        cancellation_type = _get_cancellation_type(policy)
        description = _get_policy_description(policy)

        return CancelResponse(
            is_cancellable=_is_cancellable(policy),
            booking_status=BookingStatus.from_value(booking.booking_status),
            itinerary=itinerary,
            details=CancellationDetails(
                cancellation_type=cancellation_type,
                description=description,
                begin_date=policy.begin_date,
                end_date=policy.end_date,
                penalty_amount=policy.penalty_amount,
                penalty_currency=policy.penalty_currency,
            ),
        )

    except Booking.DoesNotExist:
        raise BookingException(
            BookingErrorCode.CANCELLATION_FAILURE,
            f"Could not find booking with ID {simplenight_locator} for last name {last_name}",
        )
    except HotelCancellationPolicy.DoesNotExist:
        raise BookingException(
            BookingErrorCode.CANCELLATION_FAILURE, "Could not find cancellation policies",
        )
    except HotelBooking.DoesNotExist:
        raise BookingException(
            BookingErrorCode.CANCELLATION_FAILURE, "Could not load hotel booking",
        )


def _get_policy_description(policy):
    description = policy.description
    if not description:
        description = "Booking is non-refundable"

    return description


def _is_cancellable(cancellation_policy):
    cancellation_type = _get_cancellation_type(cancellation_policy)
    if cancellation_type in [CancellationSummary.FREE_CANCELLATION, CancellationSummary.PARTIAL_REFUND]:
        return True

    return False


def _get_cancellation_type(policy):
    cancellation_type = CancellationSummary.NON_REFUNDABLE
    if policy.cancellation_type:
        cancellation_type = CancellationSummary.from_value(policy.cancellation_type)
    return cancellation_type


def _find_active_cancellation_policy(booking_id):
    current_date = datetime.now().date()
    cancellation_policies = HotelCancellationPolicy.objects.filter(hotel_booking__booking__booking_id=booking_id)
    if len(cancellation_policies) == 1:
        return cancellation_policies[0]

    for policy in cancellation_policies:
        if policy.begin_date < current_date < policy.end_date:
            return policy

    raise BookingException(BookingErrorCode.CANCELLATION_FAILURE, "Could not find eligible cancellation policy")


def _create_itinerary(hotel_booking):
    return HotelItineraryItem(
        name=hotel_booking.hotel_name,
        price=Money(amount=hotel_booking.total_price, currency=hotel_booking.currency),
        confirmation=hotel_booking.record_locator,
        start_date=hotel_booking.checkin,
        end_date=hotel_booking.checkout,
        address=_get_itinerary_address(hotel_booking),
    )


def _get_itinerary_address(hotel_booking):
    hotel = ProviderHotel.objects.filter(
        provider=hotel_booking.provider, provider_code=hotel_booking.provider_hotel_id, language_code="en"
    )

    if len(hotel) > 0:
        return hotel[0].get_address()


def cancel_confirm(cancel_request: CancelRequest) -> CancelConfirmResponse:
    simplenight_locator = cancel_request.booking_id
    last_name = cancel_request.last_name

    try:
        booking = _find_booking_with_booking_id_and_lastname(simplenight_locator, last_name)
        original_payment = PaymentTransaction.objects.get(booking_id=booking.booking_id)
        hotel_bookings = list(HotelBooking.objects.filter(booking_id=booking.booking_id))
        traveler = booking.lead_traveler

        booking_status = BookingStatus.from_value(booking.booking_status)
        if booking_status != BookingStatus.BOOKED:
            raise BookingException(BookingErrorCode.CANCELLATION_FAILURE, "Booking is not currently active")

        cancellation_policy = _find_active_cancellation_policy(booking.booking_id)
        if not _is_cancellable(cancellation_policy):
            raise BookingException(BookingErrorCode.CANCELLATION_FAILURE, "Booking is not cancellable")

        adapter_cancellation_response = adapter_cancel(hotel_bookings[0], traveler)
        refund_transaction = payment_service.refund_payment(
            charge_id=original_payment.charge_id, amount=original_payment.transaction_amount
        )

        refund_transaction.booking = booking
        refund_transaction.save()

        booking.booking_status = BookingStatus.CANCELLED.value
        booking.save()

        return CancelConfirmResponse(
            booking_id=str(booking.booking_id),
            booking_status=BookingStatus.CANCELLED,
            cancelled=adapter_cancellation_response.is_cancelled,
        )

    except HotelBooking.DoesNotExist:
        raise BookingException(
            BookingErrorCode.CANCELLATION_FAILURE,
            f"Could not find booking with ID {simplenight_locator} for last name {last_name}",
        )
    except Booking.DoesNotExist:
        raise BookingException(
            BookingErrorCode.CANCELLATION_FAILURE,
            f"Could not find booking with ID {simplenight_locator} for last name {last_name}",
        )
    except HotelCancellationPolicy.DoesNotExist:
        raise BookingException(
            BookingErrorCode.CANCELLATION_FAILURE, "Could not find cancellation policies",
        )


def _find_booking_with_booking_id_and_lastname(booking_id, last_name):
    return Booking.objects.get(
        recordlocator__record_locator=booking_id, lead_traveler__last_name__iexact=last_name
    )


def adapter_cancel(hotel_booking: HotelBooking, traveler: Traveler):
    hotel_booking = hotel_booking
    adapter_cancel_request = AdapterCancelRequest(
        hotel_id=hotel_booking.provider_hotel_id,
        record_locator=hotel_booking.record_locator,
        email_address=traveler.email_address,
    )

    adapter = adapter_service.get_adapter(hotel_booking.provider.name)
    return adapter.cancel(adapter_cancel_request)


def _set_booked_status(booking: Booking):
    logger.info(f"Updating booking {booking.booking_id} to BOOKED status")
    booking.booking_status = BookingStatus.BOOKED.value
    booking.save()


def _persist_booking_record(booking_request, traveler):
    booking = models.Booking(
        booking_status=BookingStatus.PENDING.value,
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
