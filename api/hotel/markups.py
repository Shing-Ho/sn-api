import uuid
from decimal import Decimal

from api.common.models import RoomRate, Money


def markup_rate(room_rate: RoomRate) -> RoomRate:
    return RoomRate(
        rate_key=str(uuid.uuid4())[-12:],
        rate_type=room_rate.rate_type,
        description=room_rate.description,
        additional_detail=room_rate.additional_detail,
        total_base_rate=markup(room_rate.total_base_rate),
        total_tax_rate=markup(room_rate.total_tax_rate),
        total=markup(room_rate.total)
    )


def markup(total: Money):
    markup_pct = Decimal("1.18")
    markup_price = round(total.amount * markup_pct, 2)

    return Money(markup_price, total.currency)
