from unittest.mock import Mock

from django.test import TestCase

from api.auth.authentication import Organization, OrganizationAPIKey, Feature
from api.common.context_middleware import RequestContextMiddleware
from api.common.request_cache import RequestCacheMiddleware


class SimplenightTestCase(TestCase):
    def setUp(self) -> None:
        self.request_cache = RequestCacheMiddleware(Mock())
        self.request_context = RequestContextMiddleware()
        self.request_cache.process_request(Mock())
        self.organization = self.create_organization()
        self.stub_feature(Feature.TEST_MODE, "true")

    def create_organization(self, organization_name="TestOrganization"):
        try:
            existing_organization = Organization.objects.get(name=organization_name)
            existing_organization.delete()
        except Organization.DoesNotExist:
            pass

        organization = Organization.objects.create(name=organization_name, api_daily_limit=1000, api_burst_limit=50)
        api_key = OrganizationAPIKey.objects.create_key(name="test-key", organization=organization)[1]

        # Since we're not executing a real request, set the organization on the context
        mock_request = Mock()
        mock_request.META = {"HTTP_X_API_KEY": api_key}
        self.request_context.process_request(mock_request)

        return organization

    def stub_feature(self, feature: Feature, value):
        self.organization.set_feature(feature, value)
