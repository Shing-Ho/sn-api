#!/usr/bin/env python
from django.core.management import BaseCommand

from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.hotel.parsers.priceline_details_parser import PricelineDetailsParser


class Command(BaseCommand):
    def handle(self, *args, **options):
        PricelineDetailsParser.remove_old_data()

        for refid in ["10046", "10047"]:
            parser = PricelineDetailsParser(transport=PricelineTransport(test_mode=True, refid=refid))
            parser.load()
