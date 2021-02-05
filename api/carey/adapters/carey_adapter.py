import warnings
from rest_framework.request import Request
from requests import Session
from typing import Dict, Any
from zeep import Client, Transport

from api.carey.settings import CONFIG
from api.common.decorators import cached_property
from api.carey.models.carey_api_model import RateInquiryRequest


class CareyAdapter:
    def get_rate_inquiry(self, rate_inquiry_request: RateInquiryRequest):
        request = self._build_request(rate_inquiry_request)
        return self.client.service.rateInquiry(**request)

    def get_book_reservation(self, book_reservation_request: Request):
        request = self._build_request(book_reservation_request)
        return self.client.service.addReservation(**request)

    def get_modify_reservation(self, modify_reservation_request: Request):
        request = self._build_request(modify_reservation_request)
        return self.client.service.modifyReservation(**request)

    def get_find_reservation(self, find_reservation_request: Request):
        request = self._build_request(find_reservation_request)
        return self.client.service.findReservation(**request)

    def get_cancel_reservation(self, cancel_reservation_request: Request):
        request = self._build_request(cancel_reservation_request)
        return self.client.service.cancelReservation(**request)

    @cached_property
    def client(self):
        return self._get_wsdl_client()

    def _create_wsdl_session(self):
        session = Session()
        self.config = CONFIG
        self.app_id = self.config["app_id"]
        self.app_key = self.config["app_key"]
        headers = {
            "Content-Type": "text/xml",
            "app_id": self.app_id,
            "app_key": self.app_key,
        }
        session.headers.update(headers)

        return session

    def _get_wsdl_client(self):

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning, 338)
            wsdl_path = self._get_wsdl_path()
            return Client(wsdl_path, transport=Transport(session=self.session))

    @staticmethod
    def _get_wsdl_path():
        wsdl_path = "https://sandbox.carey.com/CSIOTAProxy_v2/CareyReservationService?wsdl"
        return wsdl_path

    @staticmethod
    def _build_request(request: RateInquiryRequest):
        build_request: Dict[Any, Any] = {
            "Version": "1.0",
            "POS": {
                "Source": {
                    "BookingChannel": {
                        "Type": "TA",
                        "CompanyName": {
                            "Code": "",
                            "CodeContext": "52969",
                            "CompanyShortName": "PM744",
                            "_value_1": "CSI - SimpleNight",
                        },
                    }
                }
            },
            "Service": {
                "Pickup": {
                    "AirportInfo": {
                        "Departure": {
                            "AirportName": request.pickUpLoacation.location_name,
                            "LocationCode": request.pickUpLoacation.location_id,
                        }
                    },
                    "Airline": {
                        "FlightDateTime": request.flightInfo.flightDate,
                        "FlightNumber": request.flightInfo.flightNum,
                        "Code": request.flightInfo.flightCode,
                    },
                    "DateTime": request.dateTime,
                },
                "Dropoff": {
                    "Address": {
                        "LocationName": request.dropOffLocation.locationName,
                        "AddressLine": request.dropOffLocation.addressLine,
                        "CityName": request.dropOffLocation.cityName,
                        "PostalCode": request.dropOffLocation.postalCode,
                        "StateProv": {
                            "_value_1": request.dropOffLocation.stateProv["value"],
                            "StateCode": request.dropOffLocation.stateProv["StateCode"],
                        },
                        "CountryName": {
                            "_value_1": request.dropOffLocation.countryName.value,
                            "Code": request.dropOffLocation.countryName.stateCode,
                        },
                        "LocationType": "address",
                    }
                },
            },
            "ServiceType": {"Code": "Point-To-Point", "Description": "ALL"},
            "PassengerPrefs": {
                "MaximumBaggage": request.bags,
                "MaximumPassengers": request.passengers,
                "GreetingSignInd": "false",
            },
        }

        return build_request

    def __init__(self):
        self.session = self._create_wsdl_session()
