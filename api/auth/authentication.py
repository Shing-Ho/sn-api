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


class OrganizationApiThrottle(SimpleRateThrottle):
    parser = KeyParser()
    scope = "user"

    def __init__(self):
        self.rate = "5/min"
        self.api_key = None
        self.organization = None
        super().__init__()

    def allow_request(self, request, view):
        if settings.DEBUG:
            return True

        key = self.parser.get(request)
        if key:
            self.api_key = OrganizationAPIKey.objects.get_from_key(key)
            self.organization = self.api_key.organization
            self.rate = self.organization.api_daily_limit
        elif request.user:
            self.organization = Organization.objects.get(username=request.user)
            self.rate = self.organization.api_daily_limit

        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        if self.organization:
            return self.organization.name

        return request.user
