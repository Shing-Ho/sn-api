from datetime import date
from typing import Optional

from api.common.common_models import SimplenightModel
from api.hotel.models.hotel_common_models import Money
from api.locations.models import Location


class AdapterActivity(SimplenightModel):
    name: str
    code: str
    description: str
    activity_date: date
    total_price: Money
    total_base: Money
    total_taxes: Money


class AdapterActivitySearch(SimplenightModel):
    begin_date: date
    end_date: date
    adults: int
    children: int
    provider: Optional[str] = None


class AdapterActivityLocationSearch(AdapterActivitySearch):
    location: Location


class AdapterActivitySpecificSearch(AdapterActivitySearch):
    activity_id: str
