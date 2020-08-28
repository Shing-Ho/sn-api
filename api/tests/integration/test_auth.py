from django.test import Client

from api.auth.models import Organization, Feature
from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase

LOCATION_ENDPOINT = "/api/v1/locations/cities"


class TestAuth(SimplenightAPITestCase):
    def _test_authentication_required(self):
        client_without_credentials = Client()
        response = client_without_credentials.get(LOCATION_ENDPOINT)
        self.assertEqual(401, response.status_code)
        self.assertEqual("Authentication credentials were not provided.", response.json()["detail"])

        key = self.create_api_key(organization_name="test")

        client = Client(HTTP_X_API_KEY=key)
        response = client.get(LOCATION_ENDPOINT)

        self.assertEqual(200, response.status_code)

    def _test_api_quota_for_anonymous_organization(self):
        key = self.create_api_key()
        client = Client(HTTP_X_API_KEY=key)

        self.assertEqual(200, client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, client.get(LOCATION_ENDPOINT).status_code)

        # Throttled after 5 requests
        self.assertEqual(429, client.get(LOCATION_ENDPOINT).status_code)

    def test_organization_features(self):
        organization = Organization.objects.create(name="foo", api_daily_limit=100, api_burst_limit=5)
        self.assertIsNone(organization.get_feature(Feature.ENABLED_CONNECTORS))