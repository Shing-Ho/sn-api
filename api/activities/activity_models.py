from datetime import date
from typing import List

from api.common.common_models import SimplenightModel
from api.hotel.models.hotel_api_model import Image
from api.hotel.models.hotel_common_models import Money


class SimplenightActivity(SimplenightModel):
    name: str
    description: str
    activity_date: date
    total_price: Money
    total_base: Money
    total_taxes: Money
    images: List[Image]
