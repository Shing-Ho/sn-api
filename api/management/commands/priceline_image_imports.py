from django.core.management import BaseCommand

from api.hotel.adapters.priceline.priceline_image_parser import PricelineImageParser


class Command(BaseCommand):
    def handle(self, *args, **options):
        PricelineImageParser().parse_and_save(limit=5000)