"""
Thin wrapper around Django cache, initially simply to control timeouts
"""
from typing import Any

from django.conf import settings
from django.core.cache import cache


# noinspection PyShadowingBuiltins
def set(key: str, value: Any):
    cache.set(key, value, timeout=_timeout())


def get(key: str):
    return cache.get(key)


def _timeout():
    return settings.CACHE_TIMEOUT
