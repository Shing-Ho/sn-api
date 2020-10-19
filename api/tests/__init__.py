import decimal

from api.common.models import Money


def to_money(amount: str, currency="USD"):
    return Money(amount=decimal.Decimal(amount), currency=currency)
