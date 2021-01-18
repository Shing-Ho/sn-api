import abc
from typing import List

from api.activities.activity_internal_models import (
    AdapterActivity,
    AdapterActivityLocationSearch,
    AdapterActivitySpecificSearch,
)
from api.common.base_adapter import BaseAdapter


class ActivityAdapter(BaseAdapter, abc.ABC):
    @abc.abstractmethod
    async def search_by_location(self, search: AdapterActivityLocationSearch) -> List[AdapterActivity]:
        pass

    @abc.abstractmethod
    async def search_by_id(self, search: AdapterActivitySpecificSearch) -> AdapterActivity:
        pass
