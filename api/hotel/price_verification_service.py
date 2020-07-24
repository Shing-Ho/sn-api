import abc
import decimal
from enum import Enum
from typing import Union, List, Dict

from api import logger
from api.common.models import RoomRate
from api.hotel.adapters import adapter_service
from api.hotel.hotel_model import Hotel, HotelPriceVerification


class PriceVerificationLogicModule(abc.ABC):
    def __init__(self, original_rates: Dict[str, RoomRate], verified_rates: Dict[str, RoomRate]):
        self.original_rates = original_rates
        self.verified_rates = verified_rates

    @abc.abstractmethod
    def compare(self) -> HotelPriceVerification:
        pass


class PriceVerificationNoPriceChangeModule(PriceVerificationLogicModule):
    def compare(self) -> HotelPriceVerification:
        original_total = decimal.Decimal(0)
        verified_total = decimal.Decimal(0)
        for rate_key, room_rate in self.original_rates.items():
            if rate_key not in self.verified_rates:
                message = "Could not find rate key in recheck response"
                logger.error({"message": message, "verified_rates": self.verified_rates})
                raise ValueError(message)

            original_total += room_rate.total.amount
            verified_total += self.verified_rates[rate_key].total.amount

        price_difference = verified_total - original_total
        allowed_difference = price_difference <= 0
        is_exact_price = price_difference == 0

        return HotelPriceVerification(
            is_allowed_change=allowed_difference,
            is_exact_price=is_exact_price,
            room_rates=list(self.verified_rates.values()),
            original_total=original_total,
            recheck_total=verified_total,
            price_difference=price_difference,
        )


class PriceVerificationModel(Enum):
    DEFAULT = PriceVerificationNoPriceChangeModule


def get_price_verification_model(
    original_rates: Dict[str, RoomRate],
    verified_rates: Dict[str, RoomRate],
    model_type: PriceVerificationModel = PriceVerificationModel.DEFAULT,
):
    model = model_type.value
    return model(original_rates, verified_rates)


def recheck(hotel: Hotel, room_rates: Union[RoomRate, List[RoomRate]]) -> HotelPriceVerification:
    """Verify room prices with a particular HotelAdapter.  Detect price changes
    between the room rates.  Apply a validator to determine if the price change is allowed.
    If price change is not allowed, return an error.
    """

    adapter = adapter_service.get_adapter(crs_name=hotel.crs)

    verified_room_rates = adapter.recheck(room_rates)
    original_room_rates_by_rate_key = _rates_by_rate_key(room_rates)
    verified_rates_by_rate_key = _rates_by_rate_key(verified_room_rates)

    model = get_price_verification_model(original_room_rates_by_rate_key, verified_rates_by_rate_key)
    return model.compare()


def _rates_by_rate_key(room_rates: List[RoomRate]) -> Dict[str, RoomRate]:
    return {x.rate_key: x for x in room_rates}
