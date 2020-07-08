from api.models.models import Geoname, GeonameAlternateName
from api.tests.integration.simplenight_api_testcase import SimplenightAPITestCase

LOCATION_ENDPOINT = "/api/v1/Locations/"


class TestLocationsView(SimplenightAPITestCase):
    def setUp(self) -> None:
        geoname_one = self._create_geoname_model(1, "Test One", "US")
        geoname_two = self._create_geoname_model(2, "Test Two", "CA")

        self._create_altname_model(1, geoname_one, "en", "Test One")
        self._create_altname_model(2, geoname_one, "es", "Prueba One")
        self._create_altname_model(3, geoname_two, "en", "Test Two")
        self._create_altname_model(4, geoname_two, "es", "Prueba Two")

    def test_authentication_required(self):
        response = self.client.get(LOCATION_ENDPOINT)
        self.assertEqual(401, response.status_code)

        self.setupCredentials()
        response = self.client.get(LOCATION_ENDPOINT)

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.json()))

    def test_locations_returned(self):
        self.setupCredentials()
        response = self.client.get(LOCATION_ENDPOINT)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.json()))
        self.assertEqual("Test One", response.json()[0]["primary_name"])
        self.assertEqual("Test Two", response.json()[1]["primary_name"])

    def test_country_filtering(self):
        self.setupCredentials()

        # All Countries
        response = self.client.get(LOCATION_ENDPOINT)
        self.assertEqual(2, len(response.json()))

        response = self.client.get(LOCATION_ENDPOINT, data=dict(country="US"))
        self.assertEqual(1, len(response.json()))
        self.assertEqual("US", response.json()[0]["iso_country_code"])

        response = self.client.get(LOCATION_ENDPOINT, data=dict(country="CA"))
        self.assertEqual(1, len(response.json()))
        self.assertEqual("CA", response.json()[0]["iso_country_code"])

    @staticmethod
    def _create_geoname_model(geoname_id, location_name, country_code):
        geoname = Geoname(
            geoname_id=geoname_id,
            location_name=location_name,
            iso_country_code=country_code,
            latitude=50.0,
            longitude=50.0,
        )

        geoname.save()
        return geoname

    @staticmethod
    def _create_altname_model(pk_id, geoname, lang_code, name):
        alternate_name = GeonameAlternateName(
            alternate_name_id=pk_id,
            geoname=geoname,
            geoname_id=geoname.geoname_id,
            iso_language_code=lang_code,
            name=name,
            is_colloquial=False,
        )

        alternate_name.save()
        return alternate_name
