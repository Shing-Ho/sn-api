from api.hotel.models.booking_model import Payment, PaymentMethod, SubmitErrorType
from api.hotel.models.hotel_common_models import Money
from api.models.models import PaymentTransaction
from api.payments import stripe_service
from api.view.exceptions import PaymentException
from common import utils


def authorize_payment(amount: Money, payment: Payment, description: str) -> PaymentTransaction:
    if payment.payment_method == PaymentMethod.PAYMENT_CARD:
        return _authorize_credit_card(amount, payment, description)
    elif payment.payment_method == PaymentMethod.PAYMENT_TOKEN:
        return _authorize_payment_token(amount, payment, description)

    raise PaymentException(SubmitErrorType.PAYMENT_PROCESSOR_ERROR, "Payment method unsupported")


def _authorize_credit_card(amount: Money, payment: Payment, description: str):
    payment_transaction = stripe_service.charge_card(
        payment=payment,
        payment_amount=utils.to_cents(amount.amount),
        currency_code=amount.currency,
        description=description,
    )

    return payment_transaction


# Hard-coded to use Stripe currently
def _authorize_payment_token(amount: Money, payment: Payment, description: str):
    payment_transaction = stripe_service.charge_token(
        payment_token=payment.payment_token,
        payment_amount=utils.to_cents(amount.amount),
        currency_code=amount.currency,
        description=description,
    )

    return payment_transaction
