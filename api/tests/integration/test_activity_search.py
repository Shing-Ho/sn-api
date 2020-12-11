from datetime import date

from api.activities import activity_search
from api.search.search_models import ActivitySpecificSearch
from api.tests.unit.simplenight_test_case import SimplenightTestCase


class TestActivitySearch(SimplenightTestCase):
    def test_activity_search(self):
        activity_date = date(2020, 1, 1)
        search = ActivitySpecificSearch(activity_date=activity_date, adults=1, children=0, activity_id="123")

        activity = activity_search.search_by_id(search)
        self.assertIsNotNone(activity)
        self.assertIsNotNone(activity.name)
        self.assertIsNotNone(activity.description)
        self.assertIsNotNone(activity.activity_date)
        self.assertIsNotNone(activity.total_price)
        self.assertIsNotNone(activity.total_base)
        self.assertIsNotNone(activity.total_taxes)
