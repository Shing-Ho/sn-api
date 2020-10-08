from unittest.mock import Mock

from api.auth.authentication import Organization, Feature
from api.common.context_middleware import RequestContextMiddleware
from api.common.request_cache import RequestCacheMiddleware
from api.hotel.adapters import adapter_service
from api.tests import test_objects
from api.tests.simplenight_api_testcase import SimplenightAPITestCase


class TestAdapterService(SimplenightAPITestCase):
    def setUp(self) -> None:
        self.request_cache = RequestCacheMiddleware(Mock())
        self.request_context = RequestContextMiddleware()

        self.request_cache.process_request(Mock())

    def test_get_adapters_to_search(self):
        search = test_objects.hotel_specific_search(adapter="xyz")
        self.assertEqual("xyz", adapter_service.get_adapters_to_search(search))

        # Organization is identified by API key in request
        api_key = self.create_api_key(organization_name="Test_Adapter_Service")
        organization = Organization.objects.get(name="Test_Adapter_Service")
        organization.set_feature(Feature.ENABLED_ADAPTERS, "foo")

        # Since we're not executing a real request, set the organization on the context
        mock_request = Mock()
        mock_request.META = {"HTTP_X_API_KEY": api_key}
        self.request_context.process_request(mock_request)

        # Without an adapter set on the search, fall back to Organization-specified adapters
        search.provider = None
        self.assertEqual("foo", adapter_service.get_adapters_to_search(search))

        # With no adapters set on the search, or organization, fall back to "stub"
        organization.clear_feature(Feature.ENABLED_ADAPTERS)
        self.assertEqual("stub", adapter_service.get_adapters_to_search(search))

    def test_get_test_mode(self):
        self.assertTrue(adapter_service.get_test_mode())  # Default to True

        # Organization is identified by API key in request
        api_key = self.create_api_key(organization_name="Test_Adapter_Service")
        organization = Organization.objects.get(name="Test_Adapter_Service")
        organization.set_feature(Feature.TEST_MODE, False)

        # Since we're not executing a real request, set the organization on the context
        mock_request = Mock()
        mock_request.META = {"HTTP_X_API_KEY": api_key}
        self.request_context.process_request(mock_request)

        self.assertFalse(adapter_service.get_test_mode())

        organization.set_feature(Feature.TEST_MODE, True)
        self.assertTrue(adapter_service.get_test_mode())

