from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase

LOCATION_ENDPOINT = "/api/v1/Locations/"


class TestAuth(SimplenightAPITestCase):
    def test_authentication_required(self):
        response = self.client.get(LOCATION_ENDPOINT)
        self.assertEqual(401, response.status_code)
        self.assertEqual("Authentication credentials were not provided.", response.json()["detail"])

        key = self.create_api_key(organization_name="test")

        self.client.credentials(HTTP_AUTHORIZATION="Api-Key " + key)
        response = self.client.get(LOCATION_ENDPOINT)

        self.assertEqual(200, response.status_code)

    def test_api_quota_for_anonymous_organization(self):
        key = self.create_api_key()
        self.client.credentials(HTTP_AUTHORIZATION="Api-Key " + key)

        self.assertEqual(200, self.client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, self.client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, self.client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, self.client.get(LOCATION_ENDPOINT).status_code)
        self.assertEqual(200, self.client.get(LOCATION_ENDPOINT).status_code)

        # Throttled after 5 requests
        self.assertEqual(429, self.client.get(LOCATION_ENDPOINT).status_code)
