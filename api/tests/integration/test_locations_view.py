from django.test import Client

from api.tests.integration import test_models
from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase

LOCATION_BY_PREFIX_ENDPOINT = "/api/v1/locations/prefix"
LOCATION_BY_ID_ENDPOINT = "/api/v1/locations/id"


class TestLocationsView(SimplenightAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        geoname_one = test_models.create_geoname_model(1, "Test One", "FOO", "US")
        geoname_two = test_models.create_geoname_model(2, "Test Two", "FOO", "CA")

        test_models.create_altname_model(1, geoname_one, "en", "Test One")
        test_models.create_altname_model(2, geoname_one, "es", "Prueba Uno")
        test_models.create_altname_model(3, geoname_two, "en", "Test Two")
        test_models.create_altname_model(4, geoname_two, "es", "Prueba Dos")

    def test_authentication_required(self):
        client_without_credentials = Client()
        response = client_without_credentials.get(LOCATION_BY_PREFIX_ENDPOINT)
        self.assertEqual(401, response.status_code)

        response = self.get(LOCATION_BY_PREFIX_ENDPOINT, prefix="Test")

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.json()))

    def test_locations_by_prefix(self):
        response = self.get(LOCATION_BY_PREFIX_ENDPOINT, prefix="Test")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.json()))
        self.assertEqual("Test One", response.json()[0]["location_name"])
        self.assertEqual(50.0, response.json()[0]["latitude"])
        self.assertEqual(50.0, response.json()[0]["longitude"])
        self.assertEqual("Test Two", response.json()[1]["location_name"])

        response = self.get(LOCATION_BY_PREFIX_ENDPOINT, prefix="Prueba Uno", lang_code="es")
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
        self.assertEqual("Prueba Uno", response.json()[0]["location_name"])

    def test_locations_by_id(self):
        response = self.get(LOCATION_BY_ID_ENDPOINT, location_id=1)
        self.assertEqual(200, response.status_code)

        location = response.json()
        self.assertEqual("Test One", location["location_name"])
        self.assertEqual("US", location["iso_country_code"])
        self.assertEqual(1, location["location_id"])
        self.assertEqual("FOO", location["province_code"])
