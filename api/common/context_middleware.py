import uuid

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from rest_framework_api_key.permissions import KeyParser

from api.auth.authentication import OrganizationAPIKey
from api.common.request_cache import get_request_cache


class RequestContextMiddleware(MiddlewareMixin):
    @classmethod
    def process_request(cls, request: HttpRequest):
        request_cache = get_request_cache()
        request_cache.set("organization", cls.get_organization_from_api_key_in_request(request))
        request_cache.set("request_id", str(uuid.uuid4()))

    @classmethod
    def get_organization_from_api_key_in_request(cls, request: HttpRequest):
        key_parser = KeyParser()
        api_key = key_parser.get(request)
        if api_key:
            organization_api_key = OrganizationAPIKey.objects.get_from_key(api_key)
            if organization_api_key:
                return organization_api_key.organization
