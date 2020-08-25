from django.test import TestCase

from api.locations.city_mapping import CityMappingService
from api.tests.integration import test_models


class TestCityMappings(TestCase):
    def test_find_unmapped_cities(self):
        test_models.create_geoname(1, "San Francisco", "CA", "US")
        test_models.create_geoname(2, "Seattle", "WA", "US")
        test_models.create_geoname(3, "New York", "NY", "US")

        provider = "priceline"
        test_models.create_provider(provider)

        test_models.create_crs_city(provider, code="10", name="San Francisco", province="CA", country="US")
        test_models.create_crs_city(provider, code="20", name="Seattle", province="WA", country="US")
        test_models.create_crs_city(provider, code="30", name="New York City", province="NY", country="US")

        mapping_service = CityMappingService(provider)

        # All cities initially unmapped
        unmapped_simplenight_cities = mapping_service.find_unmapped_simplenight_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_simplenight_cities) == 3
        assert len(unmapped_provider_cities) == 3

        # One city is mapped
        test_models.create_city_mapping(provider, simplenight_id="1", provider_id="10")
        unmapped_simplenight_cities = mapping_service.find_unmapped_simplenight_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_simplenight_cities) == 2
        assert len(unmapped_provider_cities) == 2

        test_models.create_city_mapping(provider, simplenight_id="2", provider_id="20")
        unmapped_simplenight_cities = mapping_service.find_unmapped_simplenight_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_simplenight_cities) == 1
        assert len(unmapped_provider_cities) == 1

        test_models.create_city_mapping(provider, simplenight_id="3", provider_id="30")
        unmapped_simplenight_cities = mapping_service.find_unmapped_simplenight_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_simplenight_cities) == 0
        assert len(unmapped_provider_cities) == 0

    def test_map_cities_exact_match(self):
        test_models.create_geoname(1, "San Francisco", "CA", "US")
        test_models.create_geoname(2, "Seattle", "WA", "US")
        test_models.create_geoname(3, "New York", "NY", "US")

        provider = "priceline"
        test_models.create_provider(provider)

        test_models.create_crs_city(provider, code="10", name="San Francisco", province="CA", country="US")
        test_models.create_crs_city(provider, code="20", name="Seattle", province="WA", country="US")
        test_models.create_crs_city(provider, code="30", name="New York", province="NY", country="US")
        test_models.create_crs_city(provider, code="40", name="Foo City", province="FO", country="US")
        test_models.create_crs_city(provider, code="50", name="Bar Town", province="BR", country="US")

        mapping_service = CityMappingService(provider)

        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_provider_cities) == 5

        mapping_service.map_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_provider_cities) == 2

        # Multiple Matches, Difference Provinces
        test_models.create_geoname(6, "Sometown", province="AA", country_code="US")
        test_models.create_geoname(7, "Sometown", province="BB", country_code="US")
        test_models.create_crs_city(provider, code="60", name="Sometown", province="AA", country="US")
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_provider_cities) == 3

        mapping_service.reload()
        mapping_service.map_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_provider_cities) == 2

        # No province, but only one city, so should be mapped
        test_models.create_geoname(8, "RandomCity", province="", country_code="US")
        test_models.create_crs_city(provider, code="80", name="RandomCity", province="", country="US")

        mapping_service.reload()
        mapping_service.map_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_provider_cities) == 2

        # No province in Provider city, and multiple city name matches in Geonames, so should be skipped
        test_models.create_geoname(9, "RandomCity", province="AA", country_code="US")
        test_models.create_geoname(10, "RandomCity", province="BB", country_code="US")
        test_models.create_crs_city(provider, code="90", name="RandomCity", province="", country="US")

        mapping_service.reload()
        mapping_service.map_cities()
        unmapped_provider_cities = mapping_service.find_unmapped_provider_cities()
        assert len(unmapped_provider_cities) == 3
        assert unmapped_provider_cities[0].location_name == "Foo City"
        assert unmapped_provider_cities[1].location_name == "Bar Town"
        assert unmapped_provider_cities[2].location_name == "RandomCity"
