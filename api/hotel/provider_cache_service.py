import hashlib
from datetime import date
from typing import List

from api.activities.activity_internal_models import AdapterActivity, ActivityDataCachePayload
from api.activities.activity_models import SimplenightActivity, ActivityVariant, UrbanDeparture
from api.common import cache_storage
from api.events.events_models import AdapterEvent, SimplenightEvent, EventDataCachePayload
from api.hotel.models.hotel_api_model import RoomDataCachePayload, AdapterHotel
from api.hotel.models.hotel_common_models import RoomRate


def save_provider_rate(hotel: AdapterHotel, room_rate: RoomRate, simplenight_rate: RoomRate):
    payload = RoomDataCachePayload(
        hotel_id=hotel.hotel_id,
        adapter_hotel=hotel,
        provider=hotel.provider,
        checkin=hotel.start_date,
        checkout=hotel.end_date,
        room_code=room_rate.code,
        provider_rate=room_rate,
        simplenight_rate=simplenight_rate,
    )

    cache_storage.set(_get_cache_key(simplenight_rate.code), payload)
    cache_storage.set(_get_cache_key(room_rate.code), simplenight_rate.code)  # To lookup SN rate with Provider rate


def save_provider_activity(adapter_activity: AdapterActivity, simplenight_activity: SimplenightActivity):
    payload = ActivityDataCachePayload(
        code=adapter_activity.code,
        provider=adapter_activity.provider,
        price=adapter_activity.total_price.amount,
        currency=adapter_activity.total_price.currency,
        adapter_activity=adapter_activity,
        simplenight_activity=simplenight_activity,
    )

    cache_storage.set(_get_cache_key(simplenight_activity.code), payload)


def save_activity_variant(activity_code: str, activity_date: date, variant: ActivityVariant):
    cache_key = _get_activity_variant_cache_cache(activity_code, activity_date, variant.code)
    cache_storage.set(cache_key, variant)


def get_activity_variant(activity_code: str, activity_date: date, variant_code: str) -> ActivityVariant:
    cache_key = _get_activity_variant_cache_cache(activity_code, activity_date, variant_code)
    return cache_storage.get(cache_key)


def _get_activity_variant_cache_cache(activity_code: str, activity_date: date, variant_code: str) -> str:
    return f"{activity_code}__{activity_date}__{variant_code}"

def save_activity_provider_data(activity_code: str, provider_data: List[UrbanDeparture]):
    cache_key = f"{activity_code}_provider_data"
    cache_storage.set(cache_key, provider_data)

def get_activity_provider_data(activity_code: str):
    cache_key = f"{activity_code}_provider_data"
    return cache_storage.get(cache_key)

def get_cached_activity(activity_code: str) -> ActivityDataCachePayload:
    provider_rate = cache_storage.get(_get_cache_key(activity_code))
    if not provider_rate:
        raise RuntimeError(f"Could not find Provider Rate for Rate Key {activity_code}")

    return provider_rate


def get_cached_room_data(simplenight_rate_code: str) -> RoomDataCachePayload:
    provider_rate = cache_storage.get(_get_cache_key(simplenight_rate_code))
    if not provider_rate:
        raise RuntimeError(f"Could not find Provider Rate for Rate Key {simplenight_rate_code}")

    return provider_rate


def get_simplenight_rate(provider_rate_code) -> RoomDataCachePayload:
    simplenight_rate_id = cache_storage.get(_get_cache_key(provider_rate_code))
    if not simplenight_rate_id:
        raise RuntimeError("Could not find Simplenight Rate ID with Provider Rate ID: " + provider_rate_code)

    return get_cached_room_data(simplenight_rate_id)


def save_provider_event(adapter_event: AdapterEvent, simplenight_event: SimplenightEvent):
    payload = EventDataCachePayload(
        code=adapter_event.code,
        provider=adapter_event.provider,
        adapter_activity=adapter_event,
        simplenight_activity=simplenight_event,
    )

    cache_storage.set(_get_cache_key(simplenight_event.code), payload)


def _get_cache_key(key) -> str:
    return hashlib.md5(key.encode("UTF-8")).hexdigest()[:16]
