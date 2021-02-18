import asyncio
import uuid
from decimal import getcontext, ROUND_UP
from typing import List

from api import logger
from api.events.event_adapter import EventAdapter
from api.events.events_models import EventAdapterLocationSearch, SimplenightEvent, AdapterEvent
from api.hotel import provider_cache_service
from api.hotel.adapters import adapter_service
from api.hotel.models.hotel_common_models import Money
from api.locations import location_service
from api.multi.multi_product_models import EventLocationSearch
from api.view.exceptions import AvailabilityException, AvailabilityErrorCode


def search_by_location(search: EventLocationSearch) -> List[SimplenightEvent]:
    events = _search_all_adapters_location(search)
    return _process_events(events)


def _adapter_location_search(search: EventLocationSearch) -> EventAdapterLocationSearch:
    """Converts an API Event Location Search to an object suitable for an event adapter"""

    location = location_service.find_city_by_simplenight_id(search.location_id)
    if not location:
        raise AvailabilityException("Could not find simplenight location", AvailabilityErrorCode.LOCATION_NOT_FOUND)

    return EventAdapterLocationSearch(**search.dict(), location=location)


def _process_events(events: List[AdapterEvent]) -> List[SimplenightEvent]:
    """Process events returned from an adapter, and return SimplenightEvent."""

    return list(map(_adapter_to_simplenight_event, events))


def _adapter_to_simplenight_event(event: AdapterEvent) -> SimplenightEvent:
    """Converts the response from an Adapter-specific Event to an API Event
    Additionally, because we don't want to expose internal details (like Provider),
    we save the adapter event to a cache.  We replace the event code with a unique code to this request
    """

    simplenight_event = SimplenightEvent(
        name=event.name,
        code=str(uuid.uuid4())[:8],
        description=event.description,
        location=event.location,
        categories=event.categories,
        images=event.images,
        items=event.items,
        seating_chart=event.seating_chart,
    )

    provider_cache_service.save_provider_event(event, simplenight_event)

    return simplenight_event


def _search_all_adapters_location(search: EventLocationSearch) -> List[AdapterEvent]:
    return list(_search_all_adapters(search, EventAdapter.search_by_location.__name__))


def _search_all_adapters(search: EventLocationSearch, fn_name: str, many=True):
    """Generic function to search all enabled adapters."""

    adapters = adapter_service.get_event_adapters_to_search(search)
    for adapter in adapters:
        try:
            adapter_search = _adapter_location_search(search)
            search_fn = getattr(adapter, fn_name)
            if many:
                yield from asyncio.run(search_fn(adapter_search))
            else:
                yield asyncio.run(search_fn(search))
        except Exception:
            logger.exception(f"Error searching {adapter.get_provider_name()}")


def _format_money(money: Money):
    getcontext().rounding = ROUND_UP
    money.amount = round(money.amount, 2)
    return money
