import csv
from contextlib import closing
from io import BytesIO
from typing import List, Sequence
from urllib.request import urlopen
from zipfile import ZipFile

from django.core.management import BaseCommand

from api import logger
from api.models.models import Geoname, GeonameAlternateName


class Command(BaseCommand):
    SUPPORTED_LANGUAGES = {"en", "es", "fr", "de", "ja", "zh", "ko", "th"}
    GEONAME_CITIES = "https://download.geonames.org/export/dump/cities15000.zip"
    GEONAME_ALT_NAMES_BASE = "https://download.geonames.org/export/dump/alternatenames/"
    GEONAME_CITIES_FILENAME = "cities15000.txt"

    def handle(self, *args, **options):
        Geoname.objects.all().delete()

        cities = {}
        for row in self._download_parse_main_db():
            geoname = self._create_geoname_model(row)
            geoname.save()
            cities[geoname.geoname_id] = geoname

        by = Geoname.objects.order_by()
        for country in list(by.values_list("iso_country_code", flat=True).distinct()):
            logger.info("Loading Geoname alternate names for " + country)

            alternate_names_rows = self._download_and_parse_languages(country)
            alternate_names = map(
                self._create_alternate_name_model, alternate_names_rows
            )

            for alternate_name_model in filter(
                self._filter_alternate_names, alternate_names
            ):
                if alternate_name_model.geoname_id in cities:
                    alternate_name_model.save()

    def _filter_alternate_names(self, alternate_name: GeonameAlternateName):
        if alternate_name.iso_language_code not in self.SUPPORTED_LANGUAGES:
            return False

        if alternate_name.is_colloquial:
            return False

        return True

    def _download_parse_main_db(self):
        archive_url = self._get_geonames_url()
        cities_file = self._get_geonames_filename()

        return self._download_and_parse(archive_url, cities_file)

    @staticmethod
    def _create_alternate_name_model(row) -> GeonameAlternateName:
        return GeonameAlternateName(
            alternate_name_id=row[0],
            geoname_id=row[1],
            iso_language_code=row[2],
            name=row[3],
            is_colloquial=(row[6] == 1),
        )

    @staticmethod
    def _create_geoname_model(row) -> Geoname:
        return Geoname(
            geoname_id=row[0],
            location_name=row[2],
            latitude=row[4],
            longitude=row[5],
            iso_country_code=row[8],
        )

    def _download_and_parse_languages(self, country_code):
        url = self._get_alternate_names_url(country_code)
        filename = self._get_alternate_names_filename(country_code)

        return self._download_and_parse(url, filename)

    def _get_alternate_names_url(self, country_code):
        base_url = self.GEONAME_ALT_NAMES_BASE
        return f"{base_url}/{country_code}.zip"

    @staticmethod
    def _get_alternate_names_filename(country_code):
        return f"{country_code}.txt"

    def _get_geonames_url(self):
        return self.GEONAME_CITIES

    def _get_geonames_filename(self):
        return self.GEONAME_CITIES_FILENAME

    @staticmethod
    def _download_and_parse(location, filename) -> List[Sequence[str]]:
        with closing(urlopen(location)) as response:
            zipfile = ZipFile(BytesIO(response.read()))
            cities_archive = zipfile.open(filename)

            lines = map(lambda x: x.decode("utf-8"), cities_archive.readlines())
            yield from csv.reader(lines, delimiter="\t")
