import unittest

from api.hotel import google_pricing_api
from api.tests.utils import load_test_resource


class TestGooglePricingApiUnit(unittest.TestCase):
    def test_parse_query(self):
        resource = load_test_resource("google-pricing-api/query.xml")
        response = google_pricing_api.parse_request(resource)

        self.assertEqual("2020-12-29", response.checkin)
        self.assertEqual(1, response.nights)
        self.assertEqual(["RA-F8738", "ON-F8692", "MX-58244"], response.hotel_codes)
