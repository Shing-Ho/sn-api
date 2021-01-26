import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from api.activities.activity_internal_models import AdapterActivityLocationSearch
from api.activities.adapters.tiqets.tiqets_activity_adapter import TiqetsActivityAdapter
from api.locations.models import Location, LocationType
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestTiqets(SimplenightTestCase):
    def x_test_search(self):
        location = Location(
            location_id="SF",
            language_code="en",
            location_name="San Francisco",
            iso_country_code="US",
            latitude=Decimal("37.774930"),
            longitude=Decimal("-122.419420"),
            location_type=LocationType.CITY,
        )

        begin_date = datetime.now() + timedelta(days=30)
        end_date = datetime.now() + timedelta(days=37)
        search = AdapterActivityLocationSearch(
            begin_date=begin_date.date(), end_date=end_date, adults=1, children=0, location=location
        )

        adapter = TiqetsActivityAdapter(test_mode=True)
        print(asyncio.run(adapter.search_by_location(search)))
