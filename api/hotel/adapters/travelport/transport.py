import json
import warnings

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Transport

from api import settings


class TravelportTransport:
    def __init__(self):
        self.secrets = self._get_secrets()
        self.session = self._create_wsdl_session()
        self.client = self._get_wsdl_client()

    def create_service(self, binding_name):
        hotel_service_url = self.secrets["url"]
        target_namespace = "http://www.travelport.com/service/hotel_v50_0"
        service_binding = f"{{{target_namespace}}}{binding_name}"

        return self.client.create_service(service_binding, hotel_service_url)

    def create_hotel_search_service(self):
        return self.create_service("HotelSuperShopperServiceBinding")

    def create_hotel_details_service(self):
        return self.create_service("HotelDetailsServiceBinding")

    def _create_wsdl_session(self):
        session = Session()
        session.auth = HTTPBasicAuth(self.secrets["username"], self.secrets["password"])

        return session

    def _get_wsdl_client(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning, 338)
            wsdl_path = self._get_wsdl_path()
            return Client(wsdl_path, transport=Transport(session=self.session))

    @staticmethod
    def _get_wsdl_path():
        return f"{settings.SITE_ROOT}/resources/travelport/Release-20.2/hotel_v50_0/Hotel.wsdl"

    @staticmethod
    def _get_secrets():
        with open(f"{settings.SITE_ROOT}/secrets/travelport.json") as f:
            return json.load(f)
