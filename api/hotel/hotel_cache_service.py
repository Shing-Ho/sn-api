import hashlib

from api.common import cache_storage
from api.common.models import RoomRate
from api.hotel.hotel_model import ProviderRoomDataCachePayload, AdapterHotel


def save_provider_rate_in_cache(hotel: AdapterHotel, room_rate: RoomRate, simplenight_rate: RoomRate):
    payload = ProviderRoomDataCachePayload(
        hotel_id=hotel.hotel_id,
        provider=hotel.provider,
        checkin=hotel.start_date,
        checkout=hotel.end_date,
        room_code=room_rate.code,
        provider_rate=room_rate,
        simplenight_rate=simplenight_rate
    )

    cache_storage.set(_get_cache_key(simplenight_rate.code), payload)
    cache_storage.set(_get_cache_key(room_rate.code), simplenight_rate.code)  # To lookup SN rate with Provider rate


def get_provider_rate(simplenight_rate_code: str) -> ProviderRoomDataCachePayload:
    provider_rate = cache_storage.get(_get_cache_key(simplenight_rate_code))
    if not provider_rate:
        raise RuntimeError(f"Could not find Provider Rate for Rate Key {simplenight_rate_code}")

    return provider_rate


def get_simplenight_rate(provider_rate_code) -> str:
    simplenight_rate_id = cache_storage.get(_get_cache_key(provider_rate_code))
    if not simplenight_rate_id:
        raise RuntimeError("Could not find Simplenight Rate ID with Provider Rate ID: " + provider_rate_code)

    return simplenight_rate_id


def _get_cache_key(key) -> str:
    return hashlib.md5(key.encode("UTF-8")).hexdigest()[:16]
