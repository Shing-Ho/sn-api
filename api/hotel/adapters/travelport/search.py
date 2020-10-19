from datetime import date
from typing import Optional, Union, Dict, Any

from api.hotel.hotel_api_model import HotelLocationSearch
from api.hotel.adapters.travelport.settings import TARGET_BRANCH


class TravelportHotelSearchBuilder:
    def __init__(self):
        self._request: Dict[Any, Any] = {
            "TargetBranch": TARGET_BRANCH,
            "BillingPointOfSaleInfo": {"OriginApplication": "Simplenight"},
            "HotelSearchModifiers": {"PermittedProviders": {"Provider": "1V"}},
            "HotelSearchLocation": {},
            "HotelStay": {},
        }

    @staticmethod
    def build(search_request: HotelLocationSearch):
        builder = TravelportHotelSearchBuilder()
        builder.hotel_location = search_request.location_id
        builder.checkin = search_request.start_date
        builder.checkout = search_request.end_date
        builder.num_rooms = search_request.num_rooms
        builder.num_adults = search_request.num_adults

        return builder.request

    @property
    def request(self):
        return self._request

    @property
    def num_adults(self) -> Optional[int]:
        return self.request["HotelSearchModifiers"].get("NumberOfAdults")

    @num_adults.setter
    def num_adults(self, num_adults: int):
        self.request["HotelSearchModifiers"]["NumberOfAdults"] = num_adults

    @property
    def num_rooms(self):
        return self.request["HotelSearchModifiers"].get("NumberOfRooms")

    @num_rooms.setter
    def num_rooms(self, num_rooms):
        self.request["HotelSearchModifiers"]["NumberOfRooms"] = num_rooms

    @property
    def hotel_location(self) -> Optional[str]:
        return self.request["HotelSearchLocation"].get("HotelLocation")

    @hotel_location.setter
    def hotel_location(self, location: str):
        self.request["HotelSearchLocation"]["HotelLocation"] = location

    @property
    def checkin(self) -> Optional[date]:
        checkin_date = self.request["HotelStay"].get("CheckinDate")
        return date.fromisoformat(checkin_date)

    @checkin.setter
    def checkin(self, checkin: Union[date, str]):
        if isinstance(checkin, date):
            checkin = str(checkin)

        self.request["HotelStay"]["CheckinDate"] = checkin

    @property
    def checkout(self) -> Optional[date]:
        checkout_date = self.request["HotelStay"].get("CheckoutDate")
        return date.fromisoformat(checkout_date)

    @checkout.setter
    def checkout(self, checkout: Union[date, str]):
        if isinstance(checkout, date):
            checkout = str(checkout)

        self.request["HotelStay"]["CheckoutDate"] = checkout
