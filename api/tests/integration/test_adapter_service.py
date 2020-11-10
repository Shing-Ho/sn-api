from api.hotel.adapters import adapter_service
from api.models.models import Feature
from api.tests import test_objects
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestAdapterService(SimplenightTestCase):
    def test_get_adapters_to_search(self):
        search = test_objects.hotel_specific_search(provider="xyz")
        self.assertEqual("xyz", adapter_service.get_adapters_to_search(search))

        self.stub_feature(Feature.ENABLED_ADAPTERS, "foo")

        search.provider = None
        self.assertEqual("foo", adapter_service.get_adapters_to_search(search))

        # With no adapters set on the search, or organization, fall back to "stub"
        self.organization.clear_feature(Feature.ENABLED_ADAPTERS)
        self.assertEqual("stub", adapter_service.get_adapters_to_search(search))

    def test_get_test_mode(self):
        self.assertTrue(adapter_service.get_test_mode())  # Default to True

        self.stub_feature(Feature.TEST_MODE, "false")
        self.assertFalse(adapter_service.get_test_mode())

        self.stub_feature(Feature.TEST_MODE, "true")
        self.assertTrue(adapter_service.get_test_mode())

        self.stub_feature(Feature.TEST_MODE, "false")
        self.assertFalse(adapter_service.get_test_mode())
