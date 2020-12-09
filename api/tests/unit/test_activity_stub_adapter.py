import unittest

from api.activities.adapters.stub_activity_adapter import StubActivityAdapter
from api.search.search_models import ActivitySearch


class TestActivityStubAdapter(unittest.TestCase):
    def test_search_by_id(self):
        adapter = StubActivityAdapter()
        results = adapter.search_by_id(ActivitySearch(adults=1, children=0))

        self.assertIsNotNone(results)
        print(results)
