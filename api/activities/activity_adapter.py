import abc
from typing import List

from api.activities.activity_internal_models import AdapterActivity
from api.common.base_adapter import BaseAdapter
from api.search.search_models import ActivitySearch


class ActivityAdapter(BaseAdapter, abc.ABC):
    @abc.abstractmethod
    async def search_by_location(self, search: ActivitySearch) -> List[AdapterActivity]:
        pass

    @abc.abstractmethod
    async def search_by_id(self, search: ActivitySearch) -> AdapterActivity:
        pass
