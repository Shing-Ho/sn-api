from django.test import TestCase

from api.hotel.adapters.priceline.priceline_transport import PricelineTransport


class TestPricelineIntegration(TestCase):
    def test_transport_test_mode(self):
        transport = PricelineTransport(test_mode=True)
        hotel_express_url = transport.endpoint(transport.Endpoint.HOTEL_EXPRESS)
        self.assertEqual("https://api-sandbox.rezserver.com/api/hotel/getExpress.Results", hotel_express_url)

        transport = PricelineTransport(test_mode=False)
        hotel_express_url = transport.endpoint(transport.Endpoint.HOTEL_EXPRESS)
        self.assertEqual("https://api.rezserver.com/api/hotel/getExpress.Results", hotel_express_url)

    def test_hotel_express_availability(self):
        transport = PricelineTransport(test_mode=True)
        # results = transport.hotel_express(city_id="800046992", checkin="2020-10-05", checkout="2020-10-10")
        results = transport.hotel_details(hotel_id="700072959")
        print(results.text)