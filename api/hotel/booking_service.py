from datetime import datetime
from decimal import Decimal
from typing import Union

from api import logger
from api.common import mail, currencies, request_context
from api.common.request_context import get_request_context
from api.hotel import price_verification_service, hotel_cache_service
from api.hotel.adapters import adapter_service
from api.hotel.models.adapter_models import AdapterCancelRequest, AdapterHotel
from api.hotel.models.booking_model import HotelBookingRequest, HotelBookingResponse, Customer, Status, Reservation
from api.hotel.models.hotel_api_model import (
    SimplenightRoomType,
    CancelRequest,
    CancelResponse,
    CancellationDetails,
    CancellationSummary,
    HotelItineraryItem,
    CancelConfirmResponse,
)
from api.hotel.models.hotel_common_models import Money, RoomRate
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
    Feature,
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

        try:
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

            _send_confirmation_email(
                hotel=provider_rate_cache_payload.adapter_hotel,
                reservation=reservation,
                payment=auth_response,
                record_locator=simplenight_record_locator,
            )

            return HotelBookingResponse(
                api_version=1,
                transaction_id=book_request.transaction_id,
                booking_id=simplenight_record_locator,
                status=Status(success=True, message="success"),
                reservation=reservation,
            )

        except Exception as e:
            logger.exception(f"Booking Error.  Refunding {auth_response.charge_id} {auth_response.transaction_amount}")
            refund(booking, auth_response, total_payment_amount.amount)
            raise BookingException(BookingErrorCode.PROVIDER_BOOKING_FAILURE, str(e))

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

    logger.info(f"Looking up cancellation policy for recloc={simplenight_locator}")

    try:
        booking = _find_booking_with_booking_id_and_lastname(simplenight_locator, last_name)
        hotel_booking = HotelBooking.objects.get(booking_id=booking.booking_id)
        policy = _find_active_cancellation_policy(booking.booking_id)
        itinerary = _create_itinerary(hotel_booking)
        cancellation_type = _get_cancellation_type(policy)
        description = _get_policy_description(policy)

        original_payment = PaymentTransaction.objects.get(booking_id=booking.booking_id)
        refund_amount = _get_refund_amount(original_payment, policy)
        penalty_amount = _get_penalty_amount(original_payment, policy)

        policy = CancelResponse(
            is_cancellable=_is_cancellable(policy),
            booking_status=BookingStatus.from_value(booking.booking_status),
            itinerary=itinerary,
            details=CancellationDetails(
                cancellation_type=cancellation_type,
                description=description,
                begin_date=policy.begin_date,
                end_date=policy.end_date,
                penalty_amount=penalty_amount,
                penalty_currency=original_payment.currency,
                refund_amount=refund_amount,
                refund_currency=original_payment.currency,
            ),
        )

        logger.info(f"Found cancellation policy: {policy}")
        return policy

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


def _get_penalty_amount(payment: PaymentTransaction, policy: HotelCancellationPolicy) -> Decimal:
    if policy.get_cancellation_type() == CancellationSummary.NON_REFUNDABLE:
        penalty_amount = payment.transaction_amount
    elif policy.get_cancellation_type() == CancellationSummary.FREE_CANCELLATION:
        penalty_amount = 0
    else:
        penalty_amount = policy.penalty_amount

    return penalty_amount


def _get_refund_amount(payment: PaymentTransaction, policy: HotelCancellationPolicy) -> Decimal:
    penalty_amount = _get_penalty_amount(payment, policy)

    refund_amount = abs(payment.transaction_amount) - abs(penalty_amount)
    return min(payment.transaction_amount, refund_amount)


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


def _find_active_cancellation_policy(booking_id) -> HotelCancellationPolicy:
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
        logger.info(f"Confirming cancellation for recloc={simplenight_locator}")
        booking = _find_booking_with_booking_id_and_lastname(simplenight_locator, last_name)
        booking_status = BookingStatus.from_value(booking.booking_status)
        if booking_status != BookingStatus.BOOKED:
            raise BookingException(BookingErrorCode.CANCELLATION_FAILURE, "Booking is not currently active")

        hotel_bookings = list(HotelBooking.objects.filter(booking_id=booking.booking_id))
        traveler = booking.lead_traveler

        cancellation_policy = _find_active_cancellation_policy(booking.booking_id)
        cancellation_type = _get_cancellation_type(cancellation_policy)
        if cancellation_type == CancellationSummary.NON_REFUNDABLE:
            raise BookingException(BookingErrorCode.CANCELLATION_FAILURE, "Booking is not cancellable")

        original_payment = PaymentTransaction.objects.get(booking_id=booking.booking_id)
        refund_amount = _get_refund_amount(original_payment, cancellation_policy)
        if refund_amount > 0 and original_payment.currency != cancellation_policy.penalty_currency:
            raise BookingException(
                BookingErrorCode.CANCELLATION_FAILURE, "Cancellation policy currency and booking do not match"
            )

        adapter_cancellation_response = adapter_cancel(hotel_bookings[0], traveler)

        if original_payment.currency != cancellation_policy.penalty_currency:
            raise BookingException(
                BookingErrorCode.CANCELLATION_FAILURE, "Cancellation policy currency and booking do not match"
            )

        refund(booking, original_payment, refund_amount)
        booking.booking_status = BookingStatus.CANCELLED.value
        booking.save()

        logger.info(f"Successfully cancelled recloc {simplenight_locator}, booking ID {booking.booking_id}")
        return CancelConfirmResponse(
            booking_id=str(booking.booking_id),
            record_locator=simplenight_locator,
            booking_status=BookingStatus.CANCELLED,
            cancelled=adapter_cancellation_response.is_cancelled,
            amount_refunded=refund_amount,
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


def refund(booking, original_payment, refund_amount):
    if refund_amount <= 0:
        logger.info(f"Not processing refund for {refund_amount}")
        return None

    refund_transaction = payment_service.refund_payment(charge_id=original_payment.charge_id, amount=refund_amount)
    refund_transaction.booking = booking
    refund_transaction.save()


def _find_booking_with_booking_id_and_lastname(booking_id, last_name):
    return Booking.objects.get(recordlocator__record_locator=booking_id, lead_traveler__last_name__iexact=last_name)


def adapter_cancel(hotel_booking: HotelBooking, traveler: Traveler):
    hotel_booking = hotel_booking
    adapter_cancel_request = AdapterCancelRequest(
        hotel_id=hotel_booking.provider_hotel_id,
        record_locator=hotel_booking.record_locator,
        email_address=traveler.email_address,
    )

    adapter = adapter_service.get_adapter(hotel_booking.provider.name)

    logger.info(f"Cancelling hotel booking {hotel_booking.hotel_booking_id} in adapter {adapter.get_provider_name()}")
    return adapter.cancel(adapter_cancel_request)


def _send_confirmation_email(
    hotel: AdapterHotel, reservation: Reservation, payment: PaymentTransaction, record_locator: str
):
    try:
        template_name = "order_confirmation"
        subject = f"Simplenight Hotel Reservation {record_locator}"
        recipient = f"{reservation.customer.first_name} {reservation.customer.last_name}"
        to_email = reservation.customer.email

        params = _generate_confirmation_email_params(hotel, reservation, payment, record_locator)

        if not _is_confirmation_email_enabled():
            logger.info(f"Not sending email without email enabled. Parameters: {params}")
            return None

        mail.send_mail(template_name, subject, recipient, to_email, variables=params)

    except Exception as e:
        logger.warn(f"Could not send confirmation email: {str(e)}")


def _generate_confirmation_email_params(
    hotel: AdapterHotel, reservation: Reservation, payment: PaymentTransaction, record_locator: str
):
    friendly_cancellation_map = {
        CancellationSummary.UNKNOWN_CANCELLATION_POLICY: "Call for cancellation details",
        CancellationSummary.FREE_CANCELLATION: "Free Cancellation",
        CancellationSummary.NON_REFUNDABLE: "Non-refundable",
        CancellationSummary.PARTIAL_REFUND: "Partially-refundable",
    }

    provider_hotel = ProviderHotel.objects.get(
        provider__name=hotel.provider, provider_code=hotel.hotel_id, language_code="en"
    )

    order_currency_symbol = currencies.get_symbol(payment.currency)

    def format_money(amount):
        return f"{order_currency_symbol}{amount:.2f}"

    resort_fees = 0
    if reservation.room_rate.postpaid_fees:
        resort_fees = reservation.room_rate.postpaid_fees.total.amount

    room_type_code = reservation.room_rate.room_type_code
    room_type = next(room_type for room_type in hotel.room_types if room_type.code == room_type_code)

    return {
        "booking_id": str(record_locator),
        "order_total": format_money(reservation.room_rate.total.amount),
        "hotel_name": hotel.hotel_details.name,
        "hotel_sub_total": format_money(reservation.room_rate.total.amount),
        "record_locator": reservation.locator.id,
        "cancellation_policy": friendly_cancellation_map.get(reservation.cancellation_details[0].cancellation_type),
        "hotel_address": provider_hotel.address_line_1,
        "checkin": "04:00pm",
        "checkout": "12:00pm",
        "resort_fee": format_money(resort_fees),
        "hotel_taxes": format_money(reservation.room_rate.total_tax_rate.amount),
        "hotel_room_type": room_type.name,
        "last_four": "0000",
        "order_base_rate": format_money(reservation.room_rate.total_base_rate.amount),
        "order_taxes": format_money(reservation.room_rate.total_tax_rate.amount),
    }


def _is_confirmation_email_enabled():
    return request_context.get_config_bool_default(Feature.EMAIL_ENABLED, False)


def _set_booked_status(booking: Booking):
    logger.info(f"Updating booking {booking.booking_id} to BOOKED status")
    booking.booking_status = BookingStatus.BOOKED.value
    booking.save()


def _persist_booking_record(booking_request, traveler):
    booking = models.Booking(
        booking_status=BookingStatus.PENDING.value,
        transaction_id=booking_request.transaction_id,
        organization=get_request_context().get_organization(),
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
