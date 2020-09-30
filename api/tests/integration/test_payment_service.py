from decimal import Decimal

import pytest
from django.test import TestCase

from api.booking.booking_model import Payment, PaymentMethod, SubmitErrorType
from api.common.models import Money, Address
from api.models.models import PaymentTransaction
from api.payments import payment_service
from api.view.exceptions import PaymentException
from api.tests import test_objects
from api.tests.online import test_stripe


class TestPaymentService(TestCase):
    def test_authorize_payment_token(self):
        payment_token = test_stripe.create_test_token("4242424242424242")

        amount = Money(Decimal("1.00"), "USD")
        payment = Payment(
            payment_card_parameters=None,
            billing_address=Address(
                address1="123 Street Way", city="San Francisco", province="CA", country="US", postal_code="94111"
            ),
            payment_token=payment_token,
            payment_method=PaymentMethod.PAYMENT_TOKEN,
        )

        payment_description = "Test Payment"

        result = payment_service.authorize_payment(amount, payment, payment_description)
        assert result.charge_id is not None

        retrieved_transaction = PaymentTransaction.objects.filter(charge_id=result.charge_id).first()
        assert retrieved_transaction.charge_id == result.charge_id
        assert retrieved_transaction.transaction_amount == Decimal("1.00")

    def test_authorize_payment_card(self):
        payment = test_objects.payment("4000000000000077")
        payment_description = "Test Payment"
        amount = Money(Decimal("1.05"), "USD")

        result = payment_service.authorize_payment(amount, payment, payment_description)
        assert result.charge_id is not None
        assert result.payment_token is not None
        assert result.payment_token.startswith("tok_")
        assert result.transaction_amount == Decimal("1.05")

    def test_invalid_payment(self):
        payment = test_objects.payment("4000000000000002")  # Card fails
        payment_description = "Failing Payment"
        amount = Money(Decimal("1.10"), "USD")

        with pytest.raises(PaymentException) as e:
            payment_service.authorize_payment(amount, payment, payment_description)

        assert e.value.error_type == SubmitErrorType.PAYMENT_DECLINED
        assert "Your card was declined" in e.value.detail
