import json
import warnings
from datetime import date
from typing import List, Dict, Optional, Any, Union

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Transport

from api import settings
from api.hotel.hotels import HotelAdapter, HotelSearchRequest, HotelAdapterHotel, HotelAddress, HotelRate
secrets = {
  "url": "https://americas.universal-api.travelport.com/B2BGateway/connect/uAPI/HotelService",
  "username": "Universal API/uAPI9027118295-d926ccdb",
  "password": "qP?34fQ%mC"
}

class TravelportHotelAdapter(HotelAdapter):
    def __init__(self):
        secrets = self._get_secrets()
        self.session = self._create_wsdl_session(secrets)
        self.service = self._create_wsdl_service(secrets["url"], self.session)

    def search(self, search_request: HotelSearchRequest) -> List[HotelAdapterHotel]:
        request = TravelportHotelSearchBuilder().build_from_search_request(search_request)
        response = self.service.service(**request)

        hotel_response = response["HotelSuperShopperResults"]
        hotels_with_rates = filter(lambda x: x["HotelRateDetail"], hotel_response)
        return list(map(self._hotel_from_response, hotels_with_rates))

    @classmethod
    def _hotel_from_response(cls, hotel):
        hotel_property = hotel["HotelProperty"]
        tax, total = cls._parse_hotel_min_max_rate(hotel)

        address, city, state, postal_code, country = hotel_property["PropertyAddress"]["Address"]
        address = HotelAddress(city, state, postal_code, country, [address])

        chain = hotel_property["HotelChain"]
        name = hotel_property["Name"]

        hotel_rate = HotelRate(total, tax)
        star_rating = cls._parse_hotel_star_rating(hotel_property)

        return HotelAdapterHotel(name, chain, address, hotel_rate, star_rating)

    @staticmethod
    def _parse_hotel_star_rating(hotel) -> Optional[int]:
        return next(map(lambda x: x.Rating, hotel["HotelRating"]), None)

    @staticmethod
    def _parse_hotel_min_max_rate(hotel):
        rate = hotel["HotelRateDetail"]
        rate = rate[0]
        total = rate["Total"][3:]
        if rate["Tax"]:
            tax = rate["Tax"][3:]
        else:
            tax = 0.00
        return tax, total

    @classmethod
    def _create_wsdl_session(cls, secrets):
        session = Session()
        session.auth = HTTPBasicAuth(secrets["username"], secrets["password"])

        return session

    @classmethod
    def _create_wsdl_service(cls, hotel_service_url, session):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning, 338)
            wsdl_path = cls._get_wsdl_path()
            client = Client(wsdl_path, transport=Transport(session=session))
        target_namespace = "http://www.travelport.com/service/hotel_v50_0"
        my_binding = "HotelSuperShopperServiceBinding"
        service_binding = f"{{{target_namespace}}}{my_binding}"

        return client.create_service(service_binding, hotel_service_url)

    @staticmethod
    def _get_wsdl_path():
        return f"{settings.SITE_ROOT}/resources/travelport/Release-20.2/hotel_v50_0/Hotel.wsdl"

    @staticmethod
    def _get_secrets():
        with open(f"{settings.SITE_ROOT}/secrets/travelport.json") as f:
            return json.load(f)


class TravelportHotelSearchBuilder:
    def __init__(self):
        self._search_object: Dict[Any, Any] = {
            "TargetBranch": "P3081850",
            "BillingPointOfSaleInfo": {"OriginApplication": "uAPI"},
            "HotelSearchModifiers": {"PermittedProviders": {"Provider": "1V"}},
            "HotelSearchLocation": {},
            "HotelStay": {},
        }

    def build_from_search_request(self, search_request: HotelSearchRequest):
        self.hotel_location = search_request.location_name
        self.num_adults = search_request.num_adults
        self.checkin = search_request.checkin_date
        self.checkout = search_request.checkout_date
        self.ratetype = search_request.ratetype
        self.language = search_request.language
        self.snpropertyid = search_request.snpropertyid
        return self.search_object




    @property
    def search_object(self):
        return self._search_object

    @property
    def num_adults(self) -> Optional[int]:
        return self.search_object["HotelSearchModifiers"].get("NumberOfAdults")

    @property
    def ratetype(self):
        return self._search_object
    @property
    def language(self):
        return self._search_object
    @property
    def snpropertyid(self):
        return self._search_object
    @ratetype.setter
    def rate(self, num_adults: str):
        self._search_object["HotelSearchModifiers"]["rateType"] = ratetype
    @language.setter
    def language(self, language: str):
        self._search_object["HotelSearchModifiers"]["Language"] = language
    @snpropertyid.setter
    def snpropertyid(self,snpropertyid: str):
        self._search_object["HotelSearchModifiers"]['SnPropertyID'] = snpropertyid




    @num_adults.setter
    def num_adults(self, num_adults: int):
        self._search_object["HotelSearchModifiers"]["NumberOfAdults"] = num_adults

    @property
    def hotel_location(self) -> Optional[str]:
        return self._search_object["HotelSearchLocation"].get("HotelLocation")

    @hotel_location.setter
    def hotel_location(self, location: str):
        self._search_object["HotelSearchLocation"]["HotelLocation"] = location

    @property
    def checkin(self) -> Optional[date]:
        checkin_date = self._search_object["HotelStay"].get("CheckinDate")
        return date.fromisoformat(checkin_date)

    @checkin.setter
    def checkin(self, checkin: Union[date, str]):
        if isinstance(checkin, date):
            checkin = str(checkin)

        self._search_object["HotelStay"]["CheckinDate"] = checkin

    @property
    def checkout(self) -> Optional[date]:
        checkout_date = self._search_object["HotelStay"].get("CheckoutDate")
        return date.fromisoformat(checkout_date)

    @checkout.setter
    def checkout(self, checkout: Union[date, str]):
        if isinstance(checkout, date):
            checkout = str(checkout)

        self._search_object["HotelStay"]["CheckoutDate"] = checkout
