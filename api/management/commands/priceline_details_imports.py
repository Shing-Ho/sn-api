#!/usr/bin/env python
from django.core.management import BaseCommand

from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.parsers.priceline_details_parser import PricelineDetailsParser


class Command(BaseCommand):
    def handle(self, *args, **options):
        transport = PricelineTransport(test_mode=True)
        parser = PricelineDetailsParser(transport=transport)

        parser.load()
