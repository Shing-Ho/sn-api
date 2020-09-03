from api.auth.models import Organization
from api.common.request_cache import get_request_cache


class RequestContext:
    """Wrapper around RequestCache for consistent key usage"""

    def __init__(self, cache):
        self.cache = cache

    def get_organization(self) -> Organization:
        return self.cache.get("organization")

    def get_request_id(self) -> str:
        return self.cache.get("request_id")


def get_request_context():
    return RequestContext(get_request_cache())
