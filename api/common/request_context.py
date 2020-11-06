import distutils.util
from collections import Callable

from api.models.models import Organization, Feature
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


def get_config(feature: Feature, transform_fn: Callable = None):
    request_context = get_request_context()
    organization = request_context.get_organization()

    feature_value = organization.get_feature(feature)
    if not feature_value:
        raise RuntimeError(f"Feature {feature.name} not found")
    elif transform_fn:
        return transform_fn(feature_value)
    else:
        return feature_value


def get_config_bool(feature: Feature):
    return get_config(feature, transform_fn=distutils.util.strtobool)
