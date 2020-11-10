import typing

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_api_key.models import AbstractAPIKey
from rest_framework_api_key.permissions import BaseHasAPIKey, KeyParser

from api.common.request_context import get_request_context
from api.models.models import Organization


class OrganizationAPIKey(AbstractAPIKey):
    class Meta:
        app_label = "api"
        db_table = "organization_api_keys"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="api_keys",)


class HasOrganizationAPIKey(BaseHasAPIKey):
    model = OrganizationAPIKey

    def authenticate(self, request: HttpRequest):
        return self.has_permission(request, None), None

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        if settings.DEBUG:
            return True

        api_key_exists = super().has_permission(request, view)
        if api_key_exists:
            return True

        request_context = get_request_context()
        organization = request_context.get_organization()
        if organization:
            return True


class OrganizationApiDailyThrottle(SimpleRateThrottle):
    parser = KeyParser()
    scope = "user"

    def __init__(self):
        self.rate = "5/min"
        super().__init__()

    def allow_request(self, request, view):
        if settings.DEBUG:
            return True

        organization = get_request_context().get_organization()
        if organization:
            self.num_requests = organization.api_daily_limit
            self.duration = 86400

        allow_request = super().allow_request(request, view)

        return allow_request

    def get_cache_key(self, request, view):
        organization = get_request_context().get_organization()
        if organization:
            return f"daily.{organization.name}"

        return f"daily.{request.user}"


class OrganizationApiBurstThrottle(SimpleRateThrottle):
    parser = KeyParser()
    scope = "user"

    def __init__(self):
        self.rate = "1/minute"
        super().__init__()

    def allow_request(self, request, view):
        if settings.DEBUG:
            return True

        organization = get_request_context().get_organization()
        if organization:
            self.num_requests = organization.api_burst_limit
            self.duration = 60

        allow_request = super().allow_request(request, view)

        return allow_request

    def get_cache_key(self, request, view):
        organization = get_request_context().get_organization()
        if organization:
            return f"burst.{organization.name}"

        return f"burst.{request.user}"