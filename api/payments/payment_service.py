from typing import Optional

from api import logger
from api.hotel.models.booking_model import Payment, PaymentMethod, SubmitErrorType
from api.common.models import Money
from api.models.models import PaymentTransaction
from api.payments import stripe_service
from api.view.exceptions import PaymentException
from common import utils


def authorize_payment(amount: Money, payment: Payment, description: str) -> Optional[PaymentTransaction]:
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

    masked_card = f"************{payment.payment_card_parameters.card_number[-4:]}"
    if payment_transaction.charge_id is not None:
        logger.info(f"Successfully charged payment card {masked_card}")
        payment_transaction.save()

    return payment_transaction


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
