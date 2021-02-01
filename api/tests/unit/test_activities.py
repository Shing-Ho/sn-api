import unittest
from datetime import date
from decimal import Decimal

from api.activities.activity_models import SimplenightActivityDetailResponse
from api.common.common_models import from_json
from api.tests.utils import load_test_resource


class TestActivities(unittest.TestCase):
    def xtest_deserialize_activity_details_supplier_api(self):
        resource = load_test_resource("tiqets/tiqets-details-response.json")
        activity_detail = from_json(resource, SimplenightActivityDetailResponse)

        self.assertEqual("974626", activity_detail.code)
        self.assertEqual("TOUR", activity_detail.type)
        self.assertEqual(["ATTRACTION"], activity_detail.categories)
        self.assertEqual("America/Los_Angeles", activity_detail.timezone)
        self.assertEqual(3, len(activity_detail.images))
        self.assertEqual("Tiqets", activity_detail.contact.name)
        self.assertEqual("info@tiqets.com", activity_detail.contact.email)
        self.assertEqual("https://www.tiqets.com", activity_detail.contact.website)
        self.assertEqual("James Wattstraat 77 1097 DL, Amsterdam, Netherlands", activity_detail.contact.address)
        self.assertAlmostEqual(37.7857182, activity_detail.locations[0].latitude, 2)
        self.assertAlmostEqual(-122.4010508, activity_detail.locations[0].longitude, 2)
        self.assertEqual("151, 3rd Street", activity_detail.locations[0].address)
        self.assertEqual("ALWAYS", activity_detail.availabilities[0].type)
        self.assertEqual("Whole Day Ticket", activity_detail.availabilities[0].label)
        self.assertEqual("MONDAY", activity_detail.availabilities[0].days[0])
        self.assertEqual([], activity_detail.availabilities[0].times)
        self.assertEqual(date(2021, 1, 21), activity_detail.availabilities[0].from_date)
        self.assertEqual(date(2021, 2, 19), activity_detail.availabilities[0].to_date)
        self.assertEqual("a9d7fb1a-70d8-3284-9a7f-decfa5116467", activity_detail.availabilities[0].uuid)
        self.assertEqual("NO_REFUND", activity_detail.cancellations[0].type)
        self.assertEqual("This product is not refundable", activity_detail.cancellations[0].label)
        self.assertEqual("ATTRACTION", activity_detail.items[0].category)
        self.assertEqual("2636", activity_detail.items[0].code)
        self.assertEqual("ACTIVE", activity_detail.items[0].status)
        self.assertEqual(Decimal("20.59"), activity_detail.items[0].price)
        self.assertEqual("NET", activity_detail.items[0].price_type)
