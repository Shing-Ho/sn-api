from django.test import Client

from api.auth.models import Organization, Feature
from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase

ENDPOINT = "/api/v1/hotels/status"


class TestAuth(SimplenightAPITestCase):
    def test_authentication_required(self):
        client_without_credentials = Client()
        response = client_without_credentials.get(ENDPOINT)
        self.assertEqual(401, response.status_code)
        self.assertEqual("Authentication credentials were not provided.", response.json()["detail"])

        key = self.create_api_key(organization_name="test")

        client = Client(HTTP_X_API_KEY=key)
        response = client.get(ENDPOINT)

        self.assertEqual(200, response.status_code)

    def test_api_quota_for_anonymous_organization(self):
        key = self.create_api_key()
        client = Client(HTTP_X_API_KEY=key)

        self.assertEqual(200, client.get(ENDPOINT).status_code)
        self.assertEqual(200, client.get(ENDPOINT).status_code)
        self.assertEqual(200, client.get(ENDPOINT).status_code)
        self.assertEqual(200, client.get(ENDPOINT).status_code)
        self.assertEqual(200, client.get(ENDPOINT).status_code)

        # Throttled after 5 requests
        self.assertEqual(429, client.get(ENDPOINT).status_code)

    def test_organization_features(self):
        organization = Organization.objects.create(name="foo", api_daily_limit=100, api_burst_limit=5)
        self.assertIsNone(organization.get_feature(Feature.ENABLED_ADAPTERS))

        organization.set_feature(Feature.ENABLED_ADAPTERS, "priceline")
        self.assertEqual("priceline", organization.get_feature(Feature.ENABLED_ADAPTERS))

    def test_status_page_request_cache(self):
        key = self.create_api_key(organization_name="Test_Organization")
        client = Client(HTTP_X_API_KEY=key)

        response = client.get(ENDPOINT)
        self.assertEqual(200, response.status_code)
        self.assertEqual("OK Test_Organization", response.data)
