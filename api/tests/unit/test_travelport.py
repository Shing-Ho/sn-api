import unittest

from api.hotel.hotels import HotelSearchRequest
from api.hotel.travelport.travelport import TravelportHotelSearchBuilder


class TestTravelport(unittest.TestCase):
    def test_hotel_search_builder(self):
        search = TravelportHotelSearchBuilder()
        search.num_adults = 1
        search.checkin = "2020-12-01"
        search.checkout = "2020-12-07"
        search.hotel_location = "SFO"

        results = search.request

        self.assertEqual("P3081850", results["TargetBranch"])
        self.assertEqual("uAPI", results["BillingPointOfSaleInfo"]["OriginApplication"])
        self.assertEqual("1V", results["HotelSearchModifiers"]["PermittedProviders"]["Provider"])
        self.assertEqual(1, results["HotelSearchModifiers"]["NumberOfAdults"])
        self.assertEqual("SFO", results["HotelSearchLocation"]["HotelLocation"])
        self.assertEqual("2020-12-01", results["HotelStay"]["CheckinDate"])
        self.assertEqual("2020-12-07", results["HotelStay"]["CheckoutDate"])

    def test_hotel_search_builder_from_search_request(self):
        search_request = HotelSearchRequest(
            location_name="SFO", checkin_date="2020-12-01", checkout_date="2020-12-07", num_adults=1
        )

        results = TravelportHotelSearchBuilder.build(search_request)

        self.assertEqual("P3081850", results["TargetBranch"])
        self.assertEqual("uAPI", results["BillingPointOfSaleInfo"]["OriginApplication"])
        self.assertEqual("1V", results["HotelSearchModifiers"]["PermittedProviders"]["Provider"])
        self.assertEqual(1, results["HotelSearchModifiers"]["NumberOfAdults"])
        self.assertEqual("SFO", results["HotelSearchLocation"]["HotelLocation"])
        self.assertEqual("2020-12-01", results["HotelStay"]["CheckinDate"])
        self.assertEqual("2020-12-07", results["HotelStay"]["CheckoutDate"])
