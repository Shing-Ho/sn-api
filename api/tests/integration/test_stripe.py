from datetime import datetime, timedelta

import pytest
import stripe
from django.test import TestCase

from api.payments import stripe_service
from api.payments.payment_models import PaymentException, PaymentError


class TestStripe(TestCase):
    def test_charge_token(self):
        payment_token = create_test_token("4242424242424242")  # Card succeeds on charge
        response = stripe_service.charge_token(
            payment_token=payment_token, payment_amount=100, currency_code="USD", description="Test charge"
        )

        assert response.charge_id is not None
        assert response.provider_name == "stripe"
        assert response.transaction_amount == 1.00
        assert response.currency == "USD"

    def test_invalid_card(self):
        payment_token = create_test_token("4000000000000002")  # Card fails on charge
        with pytest.raises(PaymentException) as e:
            stripe_service.charge_token(
                payment_token=payment_token, payment_amount=100, currency_code="USD", description="Test charge"
            )

        assert e.value.error_type == PaymentError.GENERAL
        assert "Your card was declined" in e.value.detail


def create_test_token(card_num):
    tokenize_request = _test_tokenize_request(card_num)
    response = stripe.Token.create(api_key=stripe_service.STRIPE_API_KEY, card=tokenize_request)
    return response["id"]


def _test_tokenize_request(card_num):
    exp_date = datetime.now().date() + timedelta(days=365)
    return {
        "number": card_num,
        "exp_month": exp_date.month,
        "exp_year": exp_date.year,
        "cvc": "314",
    }
