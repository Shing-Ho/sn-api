import typing

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_api_key.models import AbstractAPIKey
from rest_framework_api_key.permissions import BaseHasAPIKey, KeyParser


class Organization(models.Model):
    class Meta:
        app_label = "api"

    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    api_daily_limit = models.IntegerField()
    api_burst_limit = models.IntegerField()


class OrganizationAPIKey(AbstractAPIKey):
    class Meta:
        app_label = "api"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="api_keys", )


class HasOrganizationAPIKey(BaseHasAPIKey):
    model = OrganizationAPIKey

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        if settings.DEBUG:
            return True

        return super().has_permission(request, view)


class OrganizationApiThrottle(SimpleRateThrottle):
    parser = KeyParser()
    scope = "user"

    def __init__(self):
        self.rate = "5/min"
        self.api_key = None
        super().__init__()

    def allow_request(self, request, view):
        if settings.DEBUG:
            return True

        key = self.parser.get_from_authorization(request)
        self.api_key = OrganizationAPIKey.objects.get_from_key(key)
        self.rate = self.api_key.organization.api_daily_limit

        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        return self.api_key.organization.name
