import uuid

from django.test import Client
from rest_framework.test import APITestCase, APIClient


class SimplenightAPITestCase(APITestCase):
    def setUp(self) -> None:
        api_key = self.create_api_key(organization_name=str(uuid.uuid4()))
        self.client = APIClient(HTTP_X_API_KEY=api_key)

    @staticmethod
    def create_api_key(organization_name="anonymous"):
        from api.auth.models import Organization, OrganizationAPIKey

        try:
            organization = Organization.objects.get(name=organization_name)
        except Organization.DoesNotExist:
            organization = Organization.objects.create(name=organization_name, api_daily_limit=100, api_burst_limit=5)

        api_key, key = OrganizationAPIKey.objects.create_key(name="test-key", organization=organization)

        return key
