from api.booking.booking_model import Payment, PaymentMethod
from api.common.models import Money


def authorize_payment(amount: Money, payment: Payment) -> bool:
    if payment.payment_method == PaymentMethod.CREDIT_CARD or payment.payment_method == PaymentMethod.PAYMENT_CARD:
        return _authorize_credit_card(amount, payment)

    elif payment.payment_method == PaymentMethod.PAYMENT_TOKEN:
        return _authorize_payment_token(amount, payment)


def _authorize_credit_card(amount: Money, payment: Payment):
    return True


def _authorize_payment_token(amount: Money, payment: Payment):
    return True
