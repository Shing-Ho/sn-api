from datetime import datetime

from api.activities.activity_models import SimplenightActivity
from api.common.common_models import from_json
from api.search.search_models import ActivityLocationSearch
from api.tests.unit.simplenight_test_case import SimplenightTestCase

SEARCH_BY_ID = "/api/v1/search/search"


class TestSearchViews(SimplenightTestCase):
    def test_activity_search(self):
        search = ActivityLocationSearch(activity_date=datetime.now(), adults=1, children=0, location_id="123")
        print(search.json())

        response = self._post(SEARCH_BY_ID, search)
        activities = from_json(response.content, SimplenightActivity, many=True)
        self.assertTrue(len(activities) > 1)
        self.assertIsNotNone(activities[0].name)

    def _post(self, endpoint, data):
        return self.client.post(path=endpoint, data=data.json(), format="json")
