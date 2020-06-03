import json
import warnings
from typing import List

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Transport

from api import settings
from api.hotel.hotels import HotelAdapter, HotelSearchRequest, HotelAdapterHotel, HotelAddress, HotelRate


class TravelportHotelAdapter(HotelAdapter):
    def __init__(self):
        secrets = self._get_secrets()
        hotel_service_url = secrets["url"]
        username = secrets["username"]
        password = secrets["password"]

        session = Session()
        session.auth = HTTPBasicAuth(username, password)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning, 338)
            wsdl_path = self._get_wsdl_path()
            client = Client(wsdl_path, transport=Transport(session=session))

        target_namespace = "http://www.travelport.com/service/hotel_v50_0"
        my_binding = "HotelSuperShopperServiceBinding"
        service_binding = f"{{{target_namespace}}}{my_binding}"
        self.service = client.create_service(service_binding, hotel_service_url)

    def search(self, search_request: HotelSearchRequest) -> List[HotelAdapterHotel]:
        request = {
            "TargetBranch": self._get_target_branch(),
            "BillingPointOfSaleInfo": {"OriginApplication": "uAPI"},
            "HotelSearchModifiers": {"NumberOfAdults": 1, "PermittedProviders": {"Provider": "1V"}, },
            "HotelSearchLocation": {"HotelLocation": search_request.location_name},
            "HotelStay": {"CheckinDate": "2020-12-15", "CheckoutDate": "2020-12-28"},
        }

        response = self.service.service(**request)
        hotel_response = response["HotelSuperShopperResults"]
        hotels_with_rates = filter(lambda x: x["HotelRateDetail"], hotel_response)
        return list(map(self._hotel_from_response, hotels_with_rates))

    @staticmethod
    def _hotel_from_response(hotel):
        hotel_property = hotel["HotelProperty"]
        rate = hotel["HotelRateDetail"]

        rate = rate[0]
        total = rate["Total"][3:]
        if rate["Tax"]:
            tax = rate["Tax"][3:]
        else:
            tax = 0.00

        address = hotel_property["PropertyAddress"]["Address"]
        chain = hotel_property["HotelChain"]
        name = hotel_property["Name"]

        address = HotelAddress("Foo", "Bar", "US", address[0])
        rate = HotelRate(total, tax)

        return HotelAdapterHotel(name, chain, address, rate)

    @staticmethod
    def _get_wsdl_path():
        return f"{settings.SITE_ROOT}/resources/travelport/Release-20.2/hotel_v50_0/Hotel.wsdl"

    @staticmethod
    def _get_secrets():
        with open(f"{settings.SITE_ROOT}/secrets/travelport.json") as f:
            return json.load(f)

    @staticmethod
    def _get_target_branch():
        return "P3081850"
