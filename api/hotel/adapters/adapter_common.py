from typing import Dict

from cachetools.func import ttl_cache

from api.hotel.models.booking_model import PaymentCardParameters, CardType, Payment, PaymentMethod
from api.hotel.models.hotel_common_models import Address
from api.models.models import ProviderChain


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


@ttl_cache(maxsize=10, ttl=86400)
def get_chain_mapping(provider_name) -> Dict[str, str]:
    chain_mappings = ProviderChain.objects.filter(provider__name=provider_name)
    return {chain_mappings.provider_code: chain_mappings.chain_name}
