import abc
from typing import List

from api.activities.activity_internal_models import AdapterActivity
from api.search.search_models import ActivitySearch


class ActivityAdapter(abc.ABC):
    @abc.abstractmethod
    async def search_by_location(self, search: ActivitySearch) -> List[AdapterActivity]:
        pass

    @abc.abstractmethod
    async def search_by_id(self, search: ActivitySearch) -> AdapterActivity:
        pass

    @classmethod
    @abc.abstractmethod
    def factory(cls, test_mode=True):
        pass
