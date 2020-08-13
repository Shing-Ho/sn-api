from django.test import TestCase

from api.locations import location_service
from api.tests.integration import test_models


class TestLocationService(TestCase):
    def setUp(self) -> None:
        super().setUp()
        geoname_sfo = test_models.create_geoname_model(1, "San Francisco", "CA", "US", population=100)
        geoname_sea = test_models.create_geoname_model(2, "Seattle", "WA", "US", population=5000)
        geoname_nyc = test_models.create_geoname_model(3, "New York", "NY", "US", population=10000)
        geoname_san = test_models.create_geoname_model(4, "San Diego", "CA", "US", population=50)

        test_models.create_altname_model(1, geoname_sfo, "en", "San Francisco")
        test_models.create_altname_model(1, geoname_sfo, "jp", "サンフランシスコ")
        test_models.create_altname_model(2, geoname_sea, "en", "Seattle")
        test_models.create_altname_model(3, geoname_nyc, "en", "New York City")
        test_models.create_altname_model(4, geoname_san, "en", "San Diego")

    def test_find_by_prefix(self):
        cities = location_service.find_by_prefix("San ")
        self.assertEqual(2, len(cities))

        self.assertEqual(1, cities[0].location_id)
        self.assertEqual("San Francisco", cities[0].location_name)
        self.assertEqual("CA", cities[0].province_code)
        self.assertEqual("US", cities[0].iso_country_code)
        self.assertEqual("en", cities[0].language_code)

        self.assertEqual(4, cities[1].location_id)
        self.assertEqual("San Diego", cities[1].location_name)
        self.assertEqual("en", cities[1].language_code)
        self.assertEqual("CA", cities[1].province_code)
        self.assertEqual("US", cities[1].iso_country_code)

        cities = location_service.find_by_prefix("No Match")
        self.assertEqual(0, len(cities))

        # noinspection PyTypeChecker
        cities = location_service.find_by_prefix(None)
        self.assertEqual(0, len(cities))

    def test_find_by_prefix_alt_language(self):
        cities = location_service.find_by_prefix("サンフラ", language_code="jp")
        self.assertEqual(1, len(cities))
        self.assertEqual("サンフランシスコ", cities[0].location_name)
        self.assertEqual("jp", cities[0].language_code)

        print(cities)

    def test_find_by_geoname_id(self):
        cities = location_service.find_by_id(1)
        self.assertEqual(1, cities.location_id)
        self.assertEqual("San Francisco", cities.location_name)
        self.assertEqual("CA", cities.province_code)
        self.assertEqual("US", cities.iso_country_code)
        self.assertEqual("en", cities.language_code)

    def test_find_by_geoname_id_alt_language(self):
        cities = location_service.find_by_id(1, language_code="jp")
        self.assertEqual(1, cities.location_id)
        self.assertEqual("サンフランシスコ", cities.location_name)
        self.assertEqual("CA", cities.province_code)
        self.assertEqual("US", cities.iso_country_code)
        self.assertEqual("jp", cities.language_code)