import stripe

from api import logger
from api.booking.booking_model import Payment
from api.models.models import PaymentTransaction
from api.payments.payment_models import PaymentException, PaymentError
from common import utils

STRIPE_API_KEY = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


def charge_token(payment_token: str, payment_amount: int, currency_code: str, description: str):
    if currency_code is None:
        currency_code = "USD"

    logger.info(f"Charging Stripe: {payment_amount} {currency_code}")
    try:
        response = stripe.Charge.create(
            api_key=STRIPE_API_KEY,
            amount=payment_amount,
            currency=currency_code,
            card=payment_token,
            description=description,
        )

        if not _is_success(response):
            logger.error(f"Could not charge Stripe: {response}")
            raise PaymentException(PaymentError.GENERAL, "Could not charge Stripe")

        return _payment_transaction(response)

    except Exception as e:
        logger.error("Exception while charging Stripe card", exc_info=e)
        raise PaymentException(PaymentError.GENERAL, detail=str(e))


def charge_card(payment: Payment, payment_amount: int, currency_code: str, description: str):
    payment_token = tokenize(payment)
    return charge_token(
        payment_token=payment_token, payment_amount=payment_amount, currency_code=currency_code, description=description
    )


def tokenize(payment: Payment) -> str:
    tokenize_request = {
        "number": payment.payment_card_parameters.card_number,
        "exp_month": payment.payment_card_parameters.expiration_month,
        "exp_year": payment.payment_card_parameters.expiration_year,
        "cvc": payment.payment_card_parameters.cvv,
    }

    response = stripe.Token.create(api_key=STRIPE_API_KEY, card=tokenize_request)
    return response["id"]


def _is_success(stripe_response):
    return stripe_response["captured"] is True


def _payment_transaction(stripe_response):
    transaction = PaymentTransaction()
    transaction.provider_name = "stripe"
    transaction.currency = str(stripe_response["currency"]).upper()
    transaction.charge_id = str(stripe_response["id"])
    transaction.transaction_amount = utils.to_dollars(stripe_response["amount"])
    transaction.transaction_status = str(stripe_response["object"])

    return transaction
