import typing
from enum import Enum

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_api_key.models import AbstractAPIKey
from rest_framework_api_key.permissions import BaseHasAPIKey, KeyParser


class Feature(Enum):
    ENABLED_ADAPTERS = "enabled_connectors"
    TEST_MODE = "test_mode"
    STRIPE_API_KEY = "stripe_api_key"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Organization(models.Model):
    class Meta:
        app_label = "api"
        db_table = "organization"

    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    username = models.CharField(max_length=32, null=True)
    api_daily_limit = models.IntegerField()
    api_burst_limit = models.IntegerField()

    def get_feature(self, feature: Feature):
        try:
            result = OrganizationFeatures.objects.get(organization_id=self.id, name=feature.value)
            return result.value
        except OrganizationFeatures.DoesNotExist:
            return None

    def set_feature(self, feature_type: Feature, value):
        feature_name = feature_type.value
        feature, _ = OrganizationFeatures.objects.get_or_create(organization_id=self.id, name=feature_name)

        feature.value = value
        feature.save()

    def clear_feature(self, feature_type: Feature):
        feature = OrganizationFeatures.objects.get(organization_id=self.id, name=feature_type.value)
        if feature:
            feature.delete()


class OrganizationFeatures(models.Model):
    class Meta:
        app_label = "api"
        db_table = "organization_features"
        unique_together = ('organization', 'name')

    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="org")
    name = models.TextField(choices=Feature.choices())
    value = models.TextField()


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

        return super().has_permission(request, view)


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
        return self.organization.name
