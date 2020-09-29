from api.hotel.adapters.priceline.priceline_image_parser import PricelineImageParser
from api.models.models import ProviderImages
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestProviderImages(SimplenightTestCase):
    def test_parse_and_save_priceline_photos(self):
        image_parser = PricelineImageParser()
        image_parser.parse_and_save(limit=50)

        images = ProviderImages.objects.all()
        self.assertEqual(5, len(images))
