from django.test import TestCase

from api.hotel.parsers.giata import GiataParser


class TestGiataOnline(TestCase):
    def test_parse_properties(self):
        giata = GiataParser()
        giata.execute()