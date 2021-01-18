import warnings
from rest_framework.request import Request
from requests import Session
from typing import Dict, Any
from zeep import Client, Transport

from api.carey.settings import CONFIG
from api.common.decorators import cached_property


class CareyAdapter:
    def get_rate_inquiry(self, rate_inquiry_request: Request):
        request = self._build_rate_inquiry_request(rate_inquiry_request)
        return self.client.service.rateInquiry(**request)

    def get_book_reservation(self, book_reservation_request: Request):
        request = self._build_book_reservation_request(book_reservation_request)
        return self.client.service.addReservation(**request)

    def get_modify_reservation(self, modify_reservation_request: Request):
        request = self._build_modify_reservation_request(modify_reservation_request)
        return self.client.service.modifyReservation(**request)

    def get_find_reservation(self, find_reservation_request: Request):
        request = self._build_find_reservation_request(find_reservation_request)
        return self.client.service.findReservation(**request)

    def get_cancel_reservation(self, cancel_reservation_request: Request):
        request = self._build_cancel_reservation_request(cancel_reservation_request)
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
    def _build_rate_inquiry_request(request):
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
            "Service": {
                "Pickup": {
                    "DateTime": "2021-01-21T03:41:00",
                    "AirportInfo": {"Departure": {"AirportName": "", "LocationCode": "SEA"}},
                },
                "Dropoff": {
                    "AirportInfo": {"Departure": {"AirportName": "", "LocationCode": "SEA"}},
                    "Airline": {"FlightDateTime": "", "FlightNumber": "SEA", "Code": ""},
                },
            },
            "ServiceType": {"Code": "Point-To-Point", "Description": "ALL"},
            "PassengerPrefs": {"MaximumBaggage": "1", "MaximumPassengers": "1", "GreetingSignInd": False},
            "RateQualifier": {"AccountID": ""},
        }

        return build_request

    @staticmethod
    def _build_book_reservation_request(request):
        build_request: Dict[Any, Any] = {
            "Version": "1.0",
            "SequenceNmbr": "200004",
            "TimeStamp": "2020-12-12T03:41:00",
            "POS": {
                "Source": {
                    "RequestorID": {"MessagePassword": "carey123", "Type": "TA", "ID": "testarranger@testnone.com"},
                    "BookingChannel": {
                        "Type": "TA",
                        "CompanyName": {
                            "_value_1": "CSI - SimpleNight",
                            "Code": "",
                            "CodeContext": "52969",
                            "CompanyShortName": "PM744",
                        },
                    },
                }
            },
            "Reference": {
                "ID": "ID",
                "Type": "TA",
                # "TPA_Extensions": {
                #     "IsGuestBooking": False,
                #     "IsDropOffTripDuration": False,
                #     "IsNextDay": False
                # }
            },
            "GroundReservation": {
                "Location": {
                    "Pickup": {
                        "DateTime": "2021-02-06T15:00:00",
                        "Address": {
                            "Latitude": "",
                            "Longitude": "",
                            "LocationName": "Four Seasons Hotel Seattle",
                            "AddressLine": "99 Union Street",
                            "CityName": "Seattle",
                            "PostalCode": "98101",
                            "StateProv": {"_value_1": "Washington", "StateCode": "WA"},
                            "CountryName": "United States",
                            "LocationType": "",
                        },
                    },
                    "Dropoff": {
                        "AirportInfo": {"Departure": {"AirportName": "", "LocationCode": "SEA"}},
                        "Airline": {"FlightDateTime": "", "FlightNumber": "SEA", "Code": ""},
                    },
                },
                "Passenger": {
                    "Primary": {
                        "PersonName": {"GivenName": "TestPax", "Surname": "TestPax"},
                        "Telephone": {"PhoneNumber": "1111111111", "PhoneUseType": "1", "CountryAccessCode": "1"},
                        "Email": "testpassenger@testnone.com",
                    }
                },
                "Service": {
                    "DisabilityVehicleInd": False,
                    "MaximumPassengers": "1",
                    "MaximumBaggage": "1",
                    "GreetingSignInd": False,
                    "ServiceLevel": {"Code": "Point-To-Point", "Description": "Premium"},
                    "VehicleType": {"Code": "ES03", "_value_1": "Executive Sedan"},
                },
                "Payments": {
                    "Payment": {
                        "PaymentTransactionTypeCode": "ByPaymentCC",
                        "PaymentCard": {
                            "ExpireDate": "03/21",
                            "CardType": {"Code": "VISA"},
                            "CardHolderName": "Name1 Surname1",
                            "Address": {
                                "AddressLine": "Address Line 1",
                                "CityName": "City Name",
                                "PostalCode": "12345",
                                "StateProv": {"StateCode": "WA", "_value_1": "Washington"},
                                "CountryName": {"Code": "US", "_value_1": "United States"},
                            },
                            "CardNumber": {"Token": "111", "PlainText": "4333333333333339"},
                        },
                    }
                },
            },
            "TPA_Extensions": {"PickUpSpecialInstructions": "Test special instructions"},
        }

        return build_request

    @staticmethod
    def _build_modify_reservation_request(request):
        build_request: Dict[Any, Any] = {
            "Version": "1",
            "SequenceNmbr": "200003",
            "POS": {
                "Source": {
                    "RequestorID": {"MessagePassword": "carey123", "Type": "TA", "ID": "testarranger@testnone.com"},
                    "BookingChannel": {
                        "Type": "TA",
                        "CompanyName": {
                            "_value_1": "CSI - SimpleNight",
                            "Code": "",
                            "CodeContext": "52969",
                            "CompanyShortName": "PM744",
                        },
                    },
                }
            },
            "Reservation": {
                "ReferenceID": {"ID": "WA10700906-1", "Type": "TA"},
                "Service": {
                    "DisabilityVehicleInd": False,
                    "MaximumPassengers": "1",
                    "MaximumBaggage": "1",
                    "GreetingSignInd": False,
                    "ServiceLevel": {"Code": "AsDirected", "Description": "Premium"},
                    "Locations": {
                        "Pickup": {
                            "DateTime": "2021-01-21T03:41:00",
                            # "Address": {
                            #     "Latitude": "40.7499427",
                            #     "Longitude": "-73.9909421",
                            #     "LocationName": "Hotel Pennsylvania",
                            #     "AddressLine": "410 7th Ave",
                            #     "CityName": "New York",
                            #     "PostalCode": "10001",
                            #     "StateProv": {
                            #         "_value_1": "New York",
                            #         "StateCode": "NY"
                            #     },
                            #     "CountryName": "United States",
                            #     "LocationType": "US"
                            # }
                        },
                        "Dropoff": {
                            "AirportInfo": {"Departure": {"AirportName": "Newark Liberty", "LocationCode": "EWR"}},
                            "Airline": {
                                "_value_1": "United Airlines",
                                "FlightDateTime": "2018-01-21T14:00:00",
                                "FlightNumber": "1902",
                                "Code": "UA",
                            },
                        },
                    },
                    "VehicleType": {"Code": "LS03", "_value_1": "Luxury Sedan"},
                },
                "Passenger": {
                    "Primary": {
                        "PersonName": {"GivenName": "TestPax", "Surname": "TestPax"},
                        "Telephone": {"PhoneNumber": "1111111111", "PhoneUseType": "1", "CountryAccessCode": "1"},
                        "Email": "testpassenger@testnone.com",
                    }
                },
                "RateQualifier": {"AccountID": "WA831732"},
            },
        }

        return build_request

    @staticmethod
    def _build_find_reservation_request(request):
        build_request: Dict[Any, Any] = {
            "Version": "1.0",
            "POS": {
                "Source": {
                    "RequestorID": {"MessagePassword": "carey123", "Type": "TA", "ID": "testarranger@testnone.com"},
                    "BookingChannel": {
                        "Type": "TA",
                        "CompanyName": {
                            "_value_1": "CSI - SimpleNight",
                            "Code": "",
                            "CodeContext": "52969",
                            "CompanyShortName": "PM744",
                        },
                    },
                }
            },
            "Reference": {
                "ID": "WA13193419-1",
                "Type": "TA",
            },
        }

        return build_request

    @staticmethod
    def _build_cancel_reservation_request(request):
        build_request: Dict[Any, Any] = {
            "Version": "1",
            "SequenceNmbr": "200003",
            "POS": {
                "Source": {
                    "RequestorID": {"MessagePassword": "carey123", "Type": "TA", "ID": "testarranger@testnone.com"},
                    "BookingChannel": {
                        "Type": "TA",
                        "CompanyName": {
                            "_value_1": "CSI - SimpleNight",
                            "Code": "",
                            "CodeContext": "52969",
                            "CompanyShortName": "PM744",
                        },
                    },
                }
            },
            "Reservation": {"UniqueID": {"Type": "TA", "ID": "WA13193419-1"}, "CancelType": "cancel"},
        }

        return build_request

    def __init__(self):
        self.session = self._create_wsdl_session()
