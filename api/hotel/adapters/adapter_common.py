from api.hotel.models.booking_model import PaymentCardParameters, CardType, Payment, PaymentMethod
from api.common.models import Address


def get_virtual_credit_card(test_mode=True) -> Payment:
    if test_mode:
        return Payment(
            payment_method=PaymentMethod.CREDIT_CARD,
            payment_card_parameters=PaymentCardParameters(
                card_type=CardType.VI,
                card_number="4242424242424242",
                cardholder_name="Simplenight Test",
                expiration_month="01",
                expiration_year="2025",
                cvv="123",
            ),
            billing_address=Address(
                city="Miami", province="FL", country="US", address1="123 Simplenight Way", postal_code="94111",
            ),
        )
    else:
        raise NotImplemented("Virtual credit card does not exist in Production")
