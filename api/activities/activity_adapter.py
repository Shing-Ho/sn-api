import abc
from datetime import date
from typing import List

from api.activities.activity_internal_models import (
    AdapterActivity,
    AdapterActivityLocationSearch,
    AdapterActivitySpecificSearch,
    AdapterActivityBookingResponse,
)
from api.common.base_adapter import BaseAdapter
from api.hotel.models.booking_model import ActivityBookingRequest


class ActivityAdapter(BaseAdapter, abc.ABC):
    @abc.abstractmethod
    async def search_by_location(self, search: AdapterActivityLocationSearch) -> List[AdapterActivity]:
        pass

    @abc.abstractmethod
    async def search_by_id(self, search: AdapterActivitySpecificSearch) -> AdapterActivity:
        pass

    @abc.abstractmethod
    async def details(self, product_id: str, date_from: date, date_to: date) -> AdapterActivityBookingResponse:
        pass

    @abc.abstractmethod
    async def booking(self, booking_request: ActivityBookingRequest) -> AdapterActivityBookingResponse:
        pass

    @abc.abstractmethod
    async def cancel(self, order_id: str) -> bool:
        pass
