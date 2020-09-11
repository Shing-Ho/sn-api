from api.common import cache_storage
from api.common.models import RoomRate
from api.hotel.hotel_model import ProviderRoomDataCachePayload, AdapterHotel


def save_provider_rate_in_cache(key: str, hotel: AdapterHotel, room_rate: RoomRate, simplenight_rate: RoomRate):
    payload = ProviderRoomDataCachePayload(
        hotel_id=hotel.hotel_id,
        provider=hotel.provider,
        checkin=hotel.start_date,
        checkout=hotel.end_date,
        room_code=room_rate.code,
        provider_rate=room_rate,
        simplenight_rate=simplenight_rate
    )

    cache_storage.set(key, payload)
    cache_storage.set(room_rate.code, key)


def get_provider_rate_from_cache(room_code: str) -> ProviderRoomDataCachePayload:
    provider_rate = cache_storage.get(room_code)
    if not provider_rate:
        raise RuntimeError(f"Could not find Provider Rate for Rate Key {room_code}")

    return provider_rate
