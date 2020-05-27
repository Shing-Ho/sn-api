import decimal

from django.test import TestCase

from api.management.commands import geonames
from api.models.models import Geoname, GeonameAlternateName
from api.tests.utils import get_test_resource_path


class TestGeonamesCommand(TestCase):
    def test_download_and_parse(self):
        cities_sample_resource = get_test_resource_path("cities-sample.zip")
        alt_names_sample_resource = get_test_resource_path("US-alternate-names-sample.zip")

        self.assertEqual(0, Geoname.objects.count())

        geonames_cmd = geonames.Command()
        geonames_cmd._get_geonames_url = lambda: f"file://{cities_sample_resource}"
        geonames_cmd._get_geonames_filename = lambda: "cities-sample.txt"
        geonames_cmd._get_alternate_names_url = lambda x: f"file://{alt_names_sample_resource}"
        geonames_cmd._get_alternate_names_filename = lambda x: f"US-alternate-names-sample.txt"
        geonames_cmd.handle()

        self.assertEqual(4, Geoname.objects.count())
        self.assertEqual(32, GeonameAlternateName.objects.count())

        model = Geoname.objects.get(geoname_id="5391959")
        self.assertEqual("San Francisco", model.location_name)
        self.assertEqual(decimal.Decimal("37.774930"), model.latitude)
        self.assertEqual(decimal.Decimal("-122.419420"), model.longitude)

        alternate_names = GeonameAlternateName.objects.filter(geoname_id="5391959").values_list()
        self.assertEqual(10, len(alternate_names))
