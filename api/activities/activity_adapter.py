import abc
from typing import List

from api.activities.activity_models import ActivityProduct
from api.search.search_models import ActivitySearch


class ActivityAdapter(abc.ABC):
    @abc.abstractmethod
    def search_by_location(self, search: ActivitySearch) -> List[ActivityProduct]:
        pass

    @abc.abstractmethod
    def search_by_id(self, search: ActivitySearch) -> ActivityProduct:
        pass
