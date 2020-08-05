from typing import Optional

from api import logger
from api.booking.booking_model import Payment, PaymentMethod
from api.common.models import Money
from api.models.models import PaymentTransaction
from api.payments import stripe_service
from api.payments.payment_models import PaymentException, PaymentError
from common import utils


def authorize_payment(amount: Money, payment: Payment, description: str) -> Optional[PaymentTransaction]:
    if payment.payment_method == PaymentMethod.PAYMENT_CARD:
        return _authorize_credit_card(amount, payment)
    elif payment.payment_method == PaymentMethod.PAYMENT_TOKEN:
        return _authorize_payment_token(amount, payment, description)

    raise PaymentException(PaymentError.INVALID_PAYMENT, "Payment method unsupported")


def _authorize_credit_card(amount: Money, payment: Payment):
    return None


# Hard-coded to use Stripe currently
def _authorize_payment_token(amount: Money, payment: Payment, description: str):
    payment_transaction = stripe_service.charge_token(
        payment_token=payment.payment_token,
        payment_amount=utils.to_cents(amount.amount),
        currency_code=amount.currency,
        description=description,
    )

    if payment_transaction.charge_id is not None:
        logger.info(f"Successfully charged payment token {payment.payment_token}")
        payment_transaction.save()

    return payment_transaction
