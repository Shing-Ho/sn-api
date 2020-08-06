import pytest
from django.test import TestCase

from api.payments import stripe_service
from api.payments.payment_models import PaymentException, PaymentError
from api.tests import test_objects


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

    def test_charge_card_without_token(self):
        payment = test_objects.payment("4242424242424242")
        response = stripe_service.charge_card(payment, 100, "USD", "Test charge")

        assert response.charge_id is not None
        assert response.provider_name == "stripe"
        assert response.transaction_amount == 1.00
        assert response.currency == "USD"


def create_test_token(card_num):
    payment = test_objects.payment(card_num)
    return stripe_service.tokenize(payment)
