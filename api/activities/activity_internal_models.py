from datetime import date

from api.common.common_models import SimplenightModel
from api.hotel.models.hotel_common_models import Money


class AdapterActivity(SimplenightModel):
    name: str
    description: str
    activity_date: date
    total_price: Money
    total_base: Money
    total_taxes: Money
