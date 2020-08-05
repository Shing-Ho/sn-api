from decimal import Decimal

from django.test import TestCase

from api.booking.booking_model import Payment, PaymentMethod
from api.common.models import Money, Address
from api.models.models import PaymentTransaction
from api.payments import payment_service
from api.tests.integration import test_stripe


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
        assert retrieved_transaction.transaction_amount == 1.00
