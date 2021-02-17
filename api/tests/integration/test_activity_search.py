from datetime import date

from api.activities import activity_service
from api.multi.multi_product_models import ActivitySpecificSearch, ActivityLocationSearch
from api.tests import model_helper
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestActivitySearch(SimplenightTestCase):
    def test_activity_search(self):
        search = ActivitySpecificSearch(
            begin_date=date(2020, 1, 1), end_date=date(2020, 1, 5), adults=1, children=0, activity_id="123"
        )

        activity = activity_service.search_by_id(search)
        self.assertIsNotNone(activity)
        self.assertIsNotNone(activity.name)
        self.assertIsNotNone(activity.description)
        self.assertIsNotNone(activity.activity_date)
        self.assertIsNotNone(activity.total_price)
        self.assertIsNotNone(activity.total_base)
        self.assertIsNotNone(activity.total_taxes)

    def test_activity_search_by_location(self):
        test_city = model_helper.create_geoname("12345", "Test City", "Test State", "US")
        model_helper.create_geoname_altname(1, test_city, "en", "Test City Alt Name")

        search = ActivityLocationSearch(
            begin_date=date(2020, 1, 1), end_date=date(2020, 1, 5), adults=1, children=0, location_id="12345"
        )

        results = activity_service.search_by_location(search)
        self.assertIsNotNone(results)

        activity = results[0]
        self.assertIsNotNone(activity)
        self.assertIsNotNone(activity.name)
        self.assertIsNotNone(activity.description)
