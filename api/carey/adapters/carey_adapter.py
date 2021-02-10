import warnings
from rest_framework.request import Request
from requests import Session
from typing import Dict, Any
from zeep import Client, Transport, xsd

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
            "api_-id": self.app_id,
            "x-api-key": self.app_key,
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
                            "_value_1": "CSI - SimpleNight",
                            "Code": "",
                            "CodeContext": "52969",
                            "CompanyShortName": "PM744",
                        },
                    }
                }
            },
            "Service": {"Pickup": {}, "Dropoff": {}},
            "ServiceType": {"Code": request.tripType, "Description": "ALL"},
            "PassengerPrefs": {
                "MaximumBaggage": request.bags,
                "MaximumPassengers": request.passengers,
                "GreetingSignInd": False,
            },
        }
        if request.pickUpLoacation.airport:
            build_request["Service"]["Pickup"].update(
                {
                    "DateTime": request.dateTime,
                    "AirportInfo": {
                        "Departure": {
                            "AirportName": request.pickUpLoacation.locationName,
                            "LocationCode": request.pickUpLoacation.airportCode,
                        }
                    },
                    "Airline": {
                        "FlightDateTime": request.flightInfo.flightDate,
                        "FlightNumber": request.flightInfo.flightNum,
                        "Code": request.flightInfo.flightCode,
                    },
                }
            )
        else:
            if request.pickUpLoacation.trainStation:
                build_request["Service"]["Pickup"].update(
                    {
                        "DateTime": request.dateTime,
                        "Address": {
                            "LocationName": request.pickUpLoacation.locationName,
                            "AddressLine": request.pickUpLoacation.addressLine,
                            "CityName": request.pickUpLoacation.cityName,
                            "PostalCode": request.pickUpLoacation.postalCode,
                            "StateProv": {
                                "_value_1": request.pickUpLoacation.stateProv["value"],
                                "StateCode": request.pickUpLoacation.stateProv["StateCode"],
                            },
                            "CountryName": {
                                "_value_1": request.pickUpLoacation.countryName.value,
                                "Code": request.pickUpLoacation.countryName.stateCode,
                            },
                            "LocationType": xsd.SkipValue,
                        },
                    }
                )
            else:
                build_request["Service"]["Pickup"].update(
                    {
                        "DateTime": request.dateTime,
                        "Address": {
                            "LocationName": request.pickUpLoacation.locationName,
                            "AddressLine": request.pickUpLoacation.addressLine,
                            "CityName": request.pickUpLoacation.cityName,
                            "PostalCode": request.pickUpLoacation.postalCode,
                            "StateProv": {
                                "_value_1": request.pickUpLoacation.stateProv["value"],
                                "StateCode": request.pickUpLoacation.stateProv["StateCode"],
                            },
                            "CountryName": {
                                "_value_1": request.pickUpLoacation.countryName.value,
                                "Code": request.pickUpLoacation.countryName.stateCode,
                            },
                            "LocationType": xsd.SkipValue,
                        },
                    }
                )

        if request.dropOffLocation.airport:
            build_request["Service"]["Pickup"].update(
                {
                    "DateTime": request.dateTime,
                    "AirportInfo": {
                        "Departure": {
                            "AirportName": request.dropOffLocation.locationName,
                            "LocationCode": request.dropOffLocation.airportCode,
                        }
                    },
                    "Airline": {"FlightDateTime": "", "FlightNumber": "", "Code": ""},
                }
            )
        else:
            if request.dropOffLocation.trainStation:
                build_request["Service"]["Pickup"].update(
                    {
                        "DateTime": request.dateTime,
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
                            "LocationType": xsd.SkipValue,
                        },
                    }
                )
            else:
                build_request["Service"]["Pickup"].update(
                    {
                        "DateTime": request.dateTime,
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
                            "LocationType": xsd.SkipValue,
                        },
                    }
                )

                # build_request["Service"].update({
                #     "Pickup": {
                #         "DateTime": "2021-02-11T03:41:00",
                #         "Address": {
                #             "LocationName": "Four Seasons Hotel Seattle",
                #             "AddressLine": "99 Union Street",
                #             "CityName": "Seattle",
                #             "PostalCode": "98101",
                #             "StateProv": {
                #                     "_value_1": "Washington",
                #                     "StateCode": "WA",
                #             },
                #             "CountryName": {
                #                 "_value_1": "United States",
                #                 "Code": "US",
                #             },
                #             'LocationType': xsd.SkipValue
                #         },
                #     },
                #     "Dropoff": {
                #         "AirportInfo": {"Departure": {"AirportName": "", "LocationCode": "SEA"}},
                #         "Airline": {"FlightDateTime": "", "FlightNumber": "SEA", "Code": ""},
                #     }
                # })
                # "Service": {
                #         "Pickup": {
                #             "DateTime": "2021-02-11T03:41:00",
                #             "Address": {
                #                 "LocationName": "Four Seasons Hotel Seattle",
                #                 "AddressLine": "99 Union Street",
                #                 "CityName": "Seattle",
                #                 "PostalCode": "98101",
                #                 "StateProv": {
                #                     "_value_1": "Washington",
                #                     "StateCode": "WA",
                #                 },
                #                 "CountryName": {
                #                     "_value_1": "United States",
                #                     "Code": "US",
                #                 },
                #                 'LocationType': xsd.SkipValue
                #             },
                #         },
                #         "Dropoff": {
                #             "AirportInfo": {"Departure": {"AirportName": "", "LocationCode": "SEA"}},
                #             "Airline": {"FlightDateTime": "", "FlightNumber": "SEA", "Code": ""},
                #         },
                #     },

        # print("build_request=======", build_request)
        return build_request

    def __init__(self):
        self.session = self._create_wsdl_session()
