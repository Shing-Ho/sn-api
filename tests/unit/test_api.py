import unittest

from api.api import settings
from django.urls import reverse


class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        settings.configure()

    def test_index(self):
        url = reverse("api.index")
