import uuid

from rest_framework.test import APITestCase, APIClient

from api.models.models import Organization, Feature


class SimplenightAPITestCase(APITestCase):
    def setUp(self) -> None:
        organization_name = str(uuid.uuid4())
        api_key = self.create_api_key(organization_name=organization_name)
        self.organization = Organization.objects.get(name=organization_name)
        self.stub_feature(Feature.TEST_MODE, "true")
        self.client = APIClient(HTTP_X_API_KEY=api_key)

    @staticmethod
    def create_api_key(organization_name="anonymous"):
        from api.auth.authentication import Organization, OrganizationAPIKey

        try:
            organization = Organization.objects.get(name=organization_name)
        except Organization.DoesNotExist:
            organization = Organization.objects.create(name=organization_name, api_daily_limit=100, api_burst_limit=5)

        api_key, key = OrganizationAPIKey.objects.create_key(name="test-key", organization=organization)

        return key

    def stub_feature(self, feature: Feature, value):
        self.organization.set_feature(feature, value)

    def post(self, endpoint, obj, content_type="application/json"):
        data = obj.json()
        return self.client.post(endpoint, data=data, content_type=content_type)

    def get(self, endpoint, **kwargs):
        return self.client.get(endpoint, data=kwargs)
