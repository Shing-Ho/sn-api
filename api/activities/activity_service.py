import asyncio
import uuid
from decimal import getcontext, ROUND_UP
from typing import List

from api.activities.activity_adapter import ActivityAdapter
from api.activities.activity_internal_models import (
    AdapterActivity,
    AdapterActivityLocationSearch,
    AdapterActivitySpecificSearch,
    AdapterActivitySearch,
)
from api.activities.activity_models import (
    SimplenightActivity,
    SimplenightActivityDetailRequest,
    SimplenightActivityDetailResponse,
    SimplenightActivityVariantRequest,
    ActivityVariants,
)
from api.hotel import provider_cache_service
from api.hotel.adapters import adapter_service
from api.hotel.models.hotel_common_models import Money
from api.locations import location_service
from api.multi.multi_product_models import ActivityLocationSearch, ActivitySpecificSearch


def search_by_location(search: ActivityLocationSearch) -> List[SimplenightActivity]:
    adapter_search = _adapter_location_search(search)
    activities = _search_all_adapters_location(adapter_search)
    return _process_activities(activities)


def search_by_id(search: ActivitySpecificSearch) -> SimplenightActivity:
    adapter_search = _adapter_specific_search(search)
    activities = _search_all_adapters_id(adapter_search)
    activities = _process_activities(activities)
    if activities:
        return activities[0]  # TODO: Unify


def details(request: SimplenightActivityDetailRequest) -> SimplenightActivityDetailResponse:
    payload = provider_cache_service.get_cached_activity(request.code)
    adapter = adapter_service.get_activity_adapter(payload.provider)
    activity_details: SimplenightActivityDetailResponse = asyncio.run(
        adapter.details(payload.code, request.date_from, request.date_to)
    )

    # Reset to
    activity_details.code = request.code
    return activity_details


def variants(request: SimplenightActivityVariantRequest) -> List[ActivityVariants]:
    payload = provider_cache_service.get_cached_activity(request.code)
    adapter = adapter_service.get_activity_adapter(payload.provider)
    activity_variants: List[ActivityVariants] = asyncio.run(adapter.variants(payload.code, request.activity_date))

    return activity_variants


def _adapter_location_search(search: ActivityLocationSearch) -> AdapterActivityLocationSearch:
    """Converts an API Activity Location Search to an object suitable for an activity adapter"""

    location = location_service.find_city_by_simplenight_id(search.location_id)
    return AdapterActivityLocationSearch(**search.dict(), location=location)


def _adapter_specific_search(search: ActivitySpecificSearch) -> AdapterActivitySpecificSearch:
    """Converts an API Activity Specific Search to an object suitable for an activity adapter"""

    return AdapterActivitySpecificSearch(**search.dict())


def _process_activities(activities: List[AdapterActivity]) -> List[SimplenightActivity]:
    """Process activities returned from an adapter, and return SimplenightActivity.
    For now this is just scaffolding.
    """

    return list(map(_adapter_to_simplenight_activity, activities))


def _adapter_to_simplenight_activity(activity: AdapterActivity) -> SimplenightActivity:
    """Converts the response from an Adapter-specific Activity to an API Activity
    Additionally, because we don't want to expose internal details (like Provider),
    we save the adapter activity to a cache.  We replace the activity code with a unique code to this request
    """

    simplenight_activity = SimplenightActivity(
        name=activity.name,
        code=str(uuid.uuid4())[:8],
        description=activity.description,
        activity_date=activity.activity_date,
        total_price=_format_money(activity.total_price),
        total_base=_format_money(activity.total_base),
        total_taxes=_format_money(activity.total_taxes),
        images=activity.images,
    )

    provider_cache_service.save_provider_activity(activity, simplenight_activity)

    return simplenight_activity


def _search_all_adapters_location(search: AdapterActivityLocationSearch) -> List[AdapterActivity]:
    return list(_search_all_adapters(search, ActivityAdapter.search_by_location.__name__))


def _search_all_adapters_id(search: AdapterActivitySearch) -> List[AdapterActivity]:
    return list(_search_all_adapters(search, ActivityAdapter.search_by_id.__name__, many=False))


def _search_all_adapters(search: AdapterActivitySearch, fn_name: str, many=True):
    """Generic function to search all enabled adapters."""

    adapters = adapter_service.get_activity_adapters_to_search(search)
    for adapter in adapters:
        search_fn = getattr(adapter, fn_name)
        if many:
            yield from asyncio.run(search_fn(search))
        else:
            yield asyncio.run(search_fn(search))


def _format_money(money: Money):
    getcontext().rounding = ROUND_UP
    money.amount = round(money.amount, 2)
    return money