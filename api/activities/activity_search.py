import asyncio
from typing import List

from api.activities.activity_adapter import ActivityAdapter
from api.activities.activity_internal_models import AdapterActivity
from api.activities.activity_models import SimplenightActivity
from api.hotel.adapters import adapter_service
from api.search.search_models import ActivitySearch, ActivityLocationSearch, ActivitySpecificSearch


def search_by_location(search: ActivityLocationSearch) -> List[SimplenightActivity]:
    activities = _search_all_adapters_location(search)
    return _process_activities(activities)


def search_by_id(search: ActivitySpecificSearch) -> SimplenightActivity:
    activities = _search_all_adapters_id(search)
    activities = _process_activities(activities)
    if activities:
        return activities[0]  # TODO: Unify


def _process_activities(activities: List[AdapterActivity]) -> List[SimplenightActivity]:
    """Process activities returned from an adapter, and return SimplenightActivity.
    For now this is just scaffolding.
    """

    return list(map(_adapter_to_simplenight_activity, activities))


def _adapter_to_simplenight_activity(activity: AdapterActivity) -> SimplenightActivity:
    return SimplenightActivity(
        name=activity.name,
        description=activity.description,
        activity_date=activity.activity_date,
        total_price=activity.total_price,
        total_base=activity.total_base,
        total_taxes=activity.total_taxes,
    )


def _search_all_adapters_location(search: ActivitySearch) -> List[AdapterActivity]:
    return list(_search_all_adapters(search, ActivityAdapter.search_by_location.__name__))


def _search_all_adapters_id(search: ActivitySearch) -> List[AdapterActivity]:
    return list(_search_all_adapters(search, ActivityAdapter.search_by_id.__name__, many=False))


def _search_all_adapters(search: ActivitySearch, fn_name: str, many=True):
    """Generic function to search all enabled adapters."""

    adapters = adapter_service.get_activity_adapters_to_search(search)
    for adapter in adapters:
        search_fn = getattr(adapter, fn_name)
        if many:
            yield from asyncio.run(search_fn(search))
        else:
            yield asyncio.run(search_fn(search))
