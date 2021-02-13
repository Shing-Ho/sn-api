import warnings
from rest_framework.request import Request
from requests import Session
from typing import Dict, Any
from zeep import Client, Transport, xsd

from api.carey.settings import CONFIG
from api.common.decorators import cached_property
from api.carey.models.carey_api_model import RateInquiryRequest, BookReservationRequest


class CareyAdapter:
    def get_rate_inquiry(self, rate_inquiry_request: RateInquiryRequest):
        request = self._build_request(rate_inquiry_request)
        return self.client.service.rateInquiry(**request)

    def get_book_reservation(self, book_reservation_request: BookReservationRequest):
        request = self._build_book_request(book_reservation_request)
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
        return build_request

    @staticmethod
    def _build_book_request(request: BookReservationRequest):
        build_book_request: Dict[Any, Any] = {
            "Version": "1.0",
            "SequenceNmbr": "200005",
            "POS": {
                "Source": {
                    "RequestorID": {
                        "MessagePassword": "carey123",
                        "Type": "TA",
                        "ID": "testarranger@testnone.com",
                    },
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
            "GroundReservation": {
                "Location": {
                    "Pickup": {
                        "DateTime": "2021-02-06T15:00:00",
                        "Address": {
                            "LocationName": "Four Seasons Hotel Seattle",
                            "AddressLine": "99 Union Street",
                            "CityName": "Seattle",
                            "PostalCode": "98101",
                            "StateProv": {"StateCode": "WA", "_value_1": "Washington"},
                            "CountryName": {"Code": "US", "_value_1": "United States"},
                            "LocationType": xsd.SkipValue,
                        },
                    },
                    "Dropoff": {
                        "AirportInfo": {"Departure": {"AirportName": "", "LocationCode": "SEA"}},
                        "Airline": {"FlightDateTime": "", "FlightNumber": "", "Code": ""},
                    },
                },
                "Passenger": {
                    "Primary": {
                        "PersonName": {
                            "GivenName": request.passengerInfo.firstName,
                            "Surname": request.passengerInfo.lastName,
                        },
                        "Telephone": {
                            "PhoneNumber": request.passengerInfo.phoneNum,
                            "PhoneUseType": "1",
                            "CountryAccessCode": "1",
                        },
                        "Email": "testpassenger@testnone.com",
                    }
                },
                "Service": {
                    "DisabilityVehicleInd": False,
                    "MaximumPassengers": request.quoteInfo.passengers,
                    "MaximumBaggage": request.quoteInfo.bags,
                    "GreetingSignInd": False,
                    "ServiceLevel": {"Code": request.quoteInfo.tripType, "Description": "Premium"},
                    "VehicleType": {
                        "_value_1": request.quoteInfo.vehicleDetails.vehicleName,
                        "Code": request.quoteInfo.vehicleDetails.vehicleCode,
                    },
                },
                "Payments": {
                    "Payment": {
                        "PaymentTransactionTypeCode": "ByPaymentCC",
                        "PaymentCard": {
                            "ExpireDate": request.paymentInfo.expDate,
                            "CardType": {"Code": request.paymentInfo.cardType},
                            "CardHolderName": request.paymentInfo.cardName,
                            "Address": {
                                "AddressLine": request.paymentInfo.billingAddress.addressLine,
                                "CityName": request.paymentInfo.billingAddress.cityName,
                                "PostalCode": request.paymentInfo.billingAddress.postalCode,
                                "StateProv": {
                                    "_value_1": request.paymentInfo.billingAddress.stateProv["value"],
                                    "StateCode": request.paymentInfo.billingAddress.stateProv["StateCode"],
                                },
                                "CountryName": {
                                    "_value_1": request.paymentInfo.billingAddress.countryName.value,
                                    "Code": request.paymentInfo.billingAddress.countryName.stateCode,
                                },
                            },
                            "CardNumber": {
                                "Token": request.paymentInfo.expCVV,
                                "PlainText": request.paymentInfo.cardNum,
                            },
                        },
                    }
                },
            },
            "TPA_Extensions": {"PickUpSpecialInstructions": request.quoteInfo.special},
        }
        # if request.quoteInfo.pickUpLoacation.airport:
        #     build_book_request["GroundReservation"]["Location"]["Pickup"].update(
        #         {
        #             "DateTime": request.quoteInfo.pickUpDate,
        #             "AirportInfo": {
        #                 "Departure": {
        #                     "AirportName": request.quoteInfo.pickUpLoacation.locationName,
        #                     "LocationCode": request.quoteInfo.pickUpLoacation.airportCode,
        #                 }
        #             },
        #             "Airline": {
        #                 "FlightDateTime": request.quoteInfo.flightInfo.flightDate,
        #                 "FlightNumber": request.quoteInfo.flightInfo.flightNum,
        #                 "Code": request.quoteInfo.flightInfo.flightCode,
        #             },
        #         }
        #     )
        # else:
        #     if request.quoteInfo.pickUpLoacation.trainStation:
        #         build_request["GroundReservation"]["Location"]["Pickup"].update(
        #             {
        #                 "DateTime": request.quoteInfo.pickUpDate,
        #                 "Address": {
        #                     "LocationName": request.quoteInfo.pickUpLoacation.locationName,
        #                     "AddressLine": request.quoteInfo.pickUpLoacation.addressLine,
        #                     "CityName": request.quoteInfo.pickUpLoacation.cityName,
        #                     "PostalCode": request.quoteInfo.pickUpLoacation.postalCode,
        #                     "StateProv": {
        #                         "_value_1": request.quoteInfo.pickUpLoacation.stateProv["value"],
        #                         "StateCode": request.quoteInfo.pickUpLoacation.stateProv["StateCode"],
        #                     },
        #                     "CountryName": {
        #                         "_value_1": request.quoteInfo.pickUpLoacation.countryName.value,
        #                         "Code": request.quoteInfo.pickUpLoacation.countryName.stateCode,
        #                     },
        #                     "LocationType": xsd.SkipValue,
        #                 },
        #             }
        #         )
        #     else:
        #         build_request["GroundReservation"]["Location"]["Pickup"].update(
        #             {
        #                 "DateTime": request.quoteInfo.pickUpDate,
        #                 "Address": {
        #                     "LocationName": request.quoteInfo.pickUpLoacation.locationName,
        #                     "AddressLine": request.quoteInfo.pickUpLoacation.addressLine,
        #                     "CityName": request.quoteInfo.pickUpLoacation.cityName,
        #                     "PostalCode": request.quoteInfo.pickUpLoacation.postalCode,
        #                     "StateProv": {
        #                         "_value_1": request.quoteInfo.pickUpLoacation.stateProv["value"],
        #                         "StateCode": request.quoteInfo.pickUpLoacation.stateProv["StateCode"],
        #                     },
        #                     "CountryName": {
        #                         "_value_1": request.quoteInfo.pickUpLoacation.countryName.value,
        #                         "Code": request.quoteInfo.pickUpLoacation.countryName.stateCode,
        #                     },
        #                     "LocationType": xsd.SkipValue,
        #                 },
        #             }
        #         )

        # if request.quoteInfo.dropOffLocation.airport:
        #     build_request["GroundReservation"]["Location"]["Pickup"].update(
        #         {
        #             "DateTime": request.quoteInfo.pickUpDate,
        #             "AirportInfo": {
        #                 "Departure": {
        #                     "AirportName": request.quoteInfo.dropOffLocation.locationName,
        #                     "LocationCode": request.quoteInfo.dropOffLocation.airportCode,
        #                 }
        #             },
        #             "Airline": {"FlightDateTime": "", "FlightNumber": "", "Code": ""},
        #         }
        #     )
        # else:
        #     if request.quoteInfo.dropOffLocation.trainStation:
        #         build_request["GroundReservation"]["Location"]["Pickup"].update(
        #             {
        #                 "DateTime": request.quoteInfo.pickUpDate,
        #                 "Address": {
        #                     "LocationName": request.quoteInfo.dropOffLocation.locationName,
        #                     "AddressLine": request.quoteInfo.dropOffLocation.addressLine,
        #                     "CityName": request.quoteInfo.dropOffLocation.cityName,
        #                     "PostalCode": request.quoteInfo.dropOffLocation.postalCode,
        #                     "StateProv": {
        #                         "_value_1": request.quoteInfo.dropOffLocation.stateProv["value"],
        #                         "StateCode": request.quoteInfo.dropOffLocation.stateProv["StateCode"],
        #                     },
        #                     "CountryName": {
        #                         "_value_1": request.quoteInfo.dropOffLocation.countryName.value,
        #                         "Code": request.quoteInfo.dropOffLocation.countryName.stateCode,
        #                     },
        #                     "LocationType": xsd.SkipValue,
        #                 },
        #             }
        #         )
        #     else:
        #         build_request["GroundReservation"]["Location"]["Pickup"].update(
        #             {
        #                 "DateTime": request.quoteInfo.pickUpDate,
        #                 "Address": {
        #                     "LocationName": request.quoteInfo.dropOffLocation.locationName,
        #                     "AddressLine": request.quoteInfo.dropOffLocation.addressLine,
        #                     "CityName": request.quoteInfo.dropOffLocation.cityName,
        #                     "PostalCode": request.quoteInfo.dropOffLocation.postalCode,
        #                     "StateProv": {
        #                         "_value_1": request.quoteInfo.dropOffLocation.stateProv["value"],
        #                         "StateCode": request.quoteInfo.dropOffLocation.stateProv["StateCode"],
        #                     },
        #                     "CountryName": {
        #                         "_value_1": request.quoteInfo.dropOffLocation.countryName.value,
        #                         "Code": request.quoteInfo.dropOffLocation.countryName.stateCode,
        #                     },
        #                     "LocationType": xsd.SkipValue,
        #                 },
        #             }
        #         )
        return build_book_request

    def __init__(self):
        self.session = self._create_wsdl_session()
