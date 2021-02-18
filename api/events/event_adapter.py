import abc

from api.common.base_adapter import BaseAdapter


class EventAdapter(BaseAdapter, abc.ABC):
    @abc.abstractmethod
    async def search_by_location(self, EventSearch):
        pass
