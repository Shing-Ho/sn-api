import warnings
from requests import Session
from zeep import Client, Transport, xsd
from api.carey.settings import CONFIG
from api.common.decorators import cached_property
from api.carey.models.carey_api_model import (
    RateInquiryRequest,
    BookReservationRequest,
    FindReservationRequest,
    CancelReservationRequest,
)


class CareyAdapter:
    def get_rate_inquiry(self, rate_inquiry_request: RateInquiryRequest):
        POS_Type = self.client.get_type("ns1:POS_Type")
        GroundLocationsType = self.client.get_type("ns1:GroundLocationsType")
        GroundLocationType = self.client.get_type("ns1:GroundLocationType")
        GroundAirportType = self.client.get_type("ns1:GroundAirportType")
        List_GroundServiceProvided = self.client.get_type("ns1:List_GroundServiceProvided")
        GroundServiceType = self.client.get_type("ns1:GroundServiceType")
        pos = POS_Type(
            Source=[
                {
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
            ]
        )
        pickUp = GroundLocationType(
            DateTime=rate_inquiry_request.dateTime,
            Address={
                "LocationName": rate_inquiry_request.pickUpLoacation.locationName,
                "AddressLine": rate_inquiry_request.pickUpLoacation.addressLine,
                "CityName": rate_inquiry_request.pickUpLoacation.cityName,
                "PostalCode": rate_inquiry_request.pickUpLoacation.postalCode,
                "StateProv": {
                    "_value_1": rate_inquiry_request.pickUpLoacation.stateProv.value,
                    "StateCode": rate_inquiry_request.pickUpLoacation.stateProv.stateCode,
                },
                "CountryName": {
                    "_value_1": rate_inquiry_request.pickUpLoacation.countryName.value,
                    "Code": rate_inquiry_request.pickUpLoacation.countryName.stateCode,
                },
                "LocationType": "address",
            },
        )
        dropOff = {}
        if rate_inquiry_request.dropOffLocation.airport:
            dropOff = GroundLocationType(
                AirportInfo={
                    "Departure": GroundAirportType(
                        AirportName=rate_inquiry_request.dropOffLocation.locationName,
                        LocationCode=rate_inquiry_request.dropOffLocation.airportCode,
                    )
                }
            )
        else:
            dropOff = GroundLocationType(
                Address={
                    "LocationName": rate_inquiry_request.dropOffLocation.locationName,
                    "AddressLine": rate_inquiry_request.dropOffLocation.addressLine,
                    "CityName": rate_inquiry_request.dropOffLocation.cityName,
                    "PostalCode": rate_inquiry_request.dropOffLocation.postalCode,
                    "StateProv": {
                        "_value_1": rate_inquiry_request.dropOffLocation.stateProv.value,
                        "StateCode": rate_inquiry_request.dropOffLocation.stateProv.stateCode,
                    },
                    "CountryName": {
                        "_value_1": rate_inquiry_request.dropOffLocation.countryName.value,
                        "Code": rate_inquiry_request.dropOffLocation.countryName.stateCode,
                    },
                    "LocationType": "address",
                }
            )

        service = GroundLocationsType(Pickup=pickUp, Dropoff=dropOff)
        service_type = List_GroundServiceProvided(Code="Point-to-Point", Description="ALL")
        passengerPrefs = GroundServiceType(
            MaximumPassengers=rate_inquiry_request.passengers, MaximumBaggage=rate_inquiry_request.bags
        )

        return self.client.service.rateInquiry(
            Version="1.0", POS=pos, Service=service, ServiceType=service_type, PassengerPrefs=passengerPrefs
        )

    def get_book_reservation(self, book_reservation_request: BookReservationRequest):
        # request: Dict[Any, Any] = {
        #     "Version": "1.0",
        #     "SequenceNmbr": "200026",
        #     "POS": {
        #         "Source": {
        #             "RequestorID": {"MessagePassword": "Carey123", "Type": "TA", "ID": "testarranger@testnone.com"},
        #             "BookingChannel": {
        #                 "Type": "TA",
        #                 "CompanyName": {
        #                     "_value_1": "CSI - SimpleNight",
        #                     "Code": "",
        #                     "CodeContext": "52969",
        #                     "CompanyShortName": "PM744",
        #                 },
        #             },
        #         }
        #     },
        #     "GroundReservation": {
        #         "Location": {
        #             "Pickup": {
        #                 "Address": {
        #                     "Latitude": "40.7526686",
        #                     "Longitude": "-73.9935648",
        #                     "LocationName": "The New Yorker Hotel",
        #                     "AddressLine": "481 8th Avenue",
        #                     "CityName": "New York",
        #                     "PostalCode": "10001",
        #                     "StateProv": {"_value_1": "New York", "StateCode": "NY"},
        #                     "CountryName": {
        #                         "_value_1": "United States",
        #                         "Code": "US",
        #                     },
        #                     "LocationType": "address",
        #                 }
        #             },
        #             "Dropoff": {
        #                 "AirportInfo": {"Departure": {"AirportName": "", "LocationCode": "JFK"}},
        #                 "Airline": {"FlightDateTime": "", "FlightNumber": "", "Code": ""},
        #             },
        #         },
        #         "Passenger": {
        #             "Primary": {
        #                 "PersonName": {"GivenName": "Test", "Surname": "Surname"},
        #                 "Telephone": {"PhoneNumber": "123123123", "PhoneUseType": "1", "CountryAccessCode": "1"},
        #                 "Email": "testetst@gmail.com",
        #             }
        #         },
        #         "Service": {
        #             "DisabilityVehicleInd": False,
        #             "MaximumPassengers": 1,
        #             "MaximumBaggage": 1,
        #             "ServiceLevel": {"Code": "Point-To-Point", "Description": "Premium"},
        #             "VehicleType": {"Code": "FS03", "_value_1": "Fuel Efficient Sedan"},
        #         },
        #         "Payments": {
        #             "Payment": {
        #                 "PaymentTransactionTypeCode": "ByPaymentCC",
        #                 "PaymentCard": {
        #                     "ExpireDate": "03/21",
        #                     "CardType": {"Code": "VISA"},
        #                     "Address": {
        #                         "AddressLine": "Address Line 1",
        #                         "CityName": "City Name 1",
        #                         "PostalCode": "12345",
        #                         "StateProv": {"StateCode": "WA", "_value_1": "Washington"},
        #                         "CountryName": {"Code": "US", "_value_1": "United States"},
        #                     },
        #                     "CardNumber": {"Token": "111", "PlainText": "4333333333333339"},
        #                 },
        #             }
        #         },
        #     },
        #     "TPA_Extensions": {"PickUpSpecialInstructions": "Test special instructions"},
        # }

        POS_Type = self.client.get_type("ns1:POS_Type")
        GroundLocationsType = self.client.get_type("ns1:GroundLocationsType")
        GroundLocationType = self.client.get_type("ns1:GroundLocationType")
        # StateProvType = self.client.get_type("ns1:StateProvType")
        # CountryNameType = self.client.get_type("ns1:CountryNameType")
        # List_GroundLocationType = self.client.get_type("ns1:List_GroundLocationType")
        GroundAirportType = self.client.get_type("ns1:GroundAirportType")
        GroundPrimaryAdditionalPassengerType = self.client.get_type("ns1:GroundPrimaryAdditionalPassengerType")
        # PersonNameType = self.client.get_type("ns1:PersonNameType")
        # EmailType = self.client.get_type("ns1:EmailType")
        GroundServiceDetailType = self.client.get_type("ns1:GroundServiceDetailType")
        List_LevelOfService = self.client.get_type("ns1:List_LevelOfService")
        # PaymentFormType = self.client.get_type("ns1:PaymentFormType")

        pos = POS_Type(
            Source=[
                {
                    "RequestorID": {"MessagePassword": "Carey123", "Type": "TA", "ID": "testarranger@testnone.com"},
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
            ]
        )

        # pickUp = GroundLocationType(
        #     DateTime=book_reservation_request.quoteInfo.pickUpDate,
        #     Address={
        #         "Latitude": "40.7526686",
        #         "Longitude": "-73.9935648",
        #         "LocationName": "The New Yorker Hotel",
        #         "AddressLine": "481 8th Avenue",
        #         "CityName": "New York",
        #         "PostalCode": "10001",
        #         "StateProv": {
        #             "_value_1": "New York",
        #             "StateCode": "NY"
        #         },
        #         "CountryName": {
        #             "_value_1": "United States",
        #             "Code": "US",
        #         },
        #         "LocationType": "address"
        #     },
        # )
        # dropOff = None
        # if book_reservation_request.quoteInfo.dropOffLocation.airport:
        #     dropOff = GroundLocationType(
        #         AirportInfo={
        #             "Departure": GroundAirportType(
        #                 AirportName="",
        #                 LocationCode="JFK",
        #             )
        #         }
        #     )
        # else:
        #     dropOff = GroundLocationType(
        #         Address={
        #             "Latitude": "40.7526686",
        #             "Longitude": "-73.9935648",
        #             "LocationName": "The New Yorker Hotel",
        #             "AddressLine": "481 8th Avenue",
        #             "CityName": "New York",
        #             "PostalCode": "10001",
        #             "StateProv": {
        #                 "_value_1": "New York",
        #                 "StateCode": "NY"
        #             },
        #             "CountryName": {
        #                 "_value_1": "United States",
        #                 "Code": "US",
        #             },
        #             "LocationType": "address"
        #         }
        #         # Address={
        #         #     "LocationName": book_reservation_request.quoteInfo.dropOffLocation.locationName,
        #         #     "AddressLine": book_reservation_request.quoteInfo.dropOffLocation.addressLine,
        #         #     "CityName": book_reservation_request.quoteInfo.dropOffLocation.cityName,
        #         #     "PostalCode": book_reservation_request.quoteInfo.dropOffLocation.postalCode,
        #         #     "StateProv": {
        #         #         "_value_1": book_reservation_request.quoteInfo.dropOffLocation.stateProv.value,
        #         #         "StateCode": book_reservation_request.quoteInfo.dropOffLocation.stateProv.stateCode,
        #         #     },
        #         #     "CountryName": {
        #         #         "_value_1": book_reservation_request.quoteInfo.dropOffLocation.countryName.value,
        #         #         "Code": book_reservation_request.quoteInfo.dropOffLocation.countryName.stateCode,
        #         #     },
        #         #     "LocationType": "address",
        #         # }
        #     )

        # location = GroundLocationsType(Pickup=pickUp, Dropoff=dropOff)
        location = GroundLocationsType(
            Pickup=GroundLocationType(
                Address={
                    "Latitude": "40.7526686",
                    "Longitude": "-73.9935648",
                    "LocationName": "The New Yorker Hotel",
                    "AddressLine": "481 8th Avenue",
                    "CityName": "New York",
                    "PostalCode": "10001",
                    "StateProv": {"_value_1": "New York", "StateCode": "NY"},
                    "CountryName": {"_value_1": "United States", "Code": "US"},
                    "LocationType": {
                        "_value_1": xsd.SkipValue,
                        "Code": xsd.SkipValue,
                        "Description": xsd.SkipValue,
                        "ResourceName": xsd.SkipValue,
                        "UniqueID": xsd.SkipValue,
                    },
                }
            ),
            Dropoff=GroundLocationType(
                AirportInfo={
                    "Departure": GroundAirportType(
                        AirportName="",
                        LocationCode="JFK",
                    )
                }
            ),
        )
        passenger = GroundPrimaryAdditionalPassengerType(
            Primary={
                "PersonName": {
                    "GivenName": book_reservation_request.passengerInfo.firstName,
                    "Surname": book_reservation_request.passengerInfo.lastName,
                },
                "Telephone": [
                    {
                        "PhoneNumber": book_reservation_request.passengerInfo.phoneNum,
                        "PhoneUseType": "1",
                        "CountryAccessCode": "1",
                    }
                ],
                "Email": [book_reservation_request.passengerInfo.email],
            }
        )
        serviceLevel = List_LevelOfService(Code="Point-To-Point", Description="Premium")
        service = GroundServiceDetailType(
            DisabilityVehicleInd=False,
            MaximumPassengers=1,
            MaximumBaggage=1,
            GreetingSignInd=False,
            ServiceLevel=serviceLevel,
            VehicleType={
                "Code": book_reservation_request.quoteInfo.vehicleDetails.vehicleCode,
                "_value_1": book_reservation_request.quoteInfo.vehicleDetails.vehicleName,
            },
        )
        paymentInfo = book_reservation_request.paymentInfo
        return self.client.service.addReservation(
            Version="1.0",
            SequenceNmbr="200027",
            POS=pos,
            GroundReservation={
                "Location": location,
                "Passenger": passenger,
                "Service": service,
                "Payments": [
                    {
                        "Payment": {
                            "PaymentTransactionTypeCode": "ByPaymentCC",
                            "PaymentCard": {
                                "ExpireDate": paymentInfo.expDate,
                                "CardType": {"Code": paymentInfo.cardType},
                                "CardHolderName": paymentInfo.cardName,
                                "Address": {
                                    "AddressLine": paymentInfo.billingAddress.addressLine,
                                    "CityName": paymentInfo.billingAddress.cityName,
                                    "PostalCode": paymentInfo.billingAddress.postalCode,
                                    "StateProv": {
                                        "_value_1": paymentInfo.billingAddress.stateProv.value,
                                        "StateCode": paymentInfo.billingAddress.stateProv.stateCode,
                                    },
                                    "CountryName": {
                                        "_value_1": paymentInfo.billingAddress.countryName.value,
                                        "Code": paymentInfo.billingAddress.countryName.stateCode,
                                    },
                                },
                                "CardNumber": {
                                    "Token": paymentInfo.expCVV,
                                    "PlainText": paymentInfo.cardNum,
                                },
                            },
                        }
                    }
                ],
            },
            TPA_Extensions={"PickUpSpecialInstructions": book_reservation_request.quoteInfo.special},
        )

    def get_find_reservation(self, find_reservation_request: FindReservationRequest):
        POS_Type = self.client.get_type("ns1:POS_Type")
        UniqueID_Type = self.client.get_type("ns1:UniqueID_Type")
        pos = POS_Type(
            Source=[
                {
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
            ]
        )
        uniqueID = UniqueID_Type(Type=xsd.SkipValue, ID=find_reservation_request.reservation_id)

        return self.client.service.findReservation(Version="1.0", POS=pos, Reference=[uniqueID])

    def get_cancel_reservation(self, cancel_reservation_request: CancelReservationRequest):
        POS_Type = self.client.get_type("ns1:POS_Type")
        UniqueID_Type = self.client.get_type("ns1:UniqueID_Type")
        pos = POS_Type(
            Source=[
                {
                    "RequestorID": {"MessagePassword": "carey123", "Type": "TA", "ID": "test@gmail.com"},
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
            ]
        )
        uniqueID = UniqueID_Type(Type=xsd.SkipValue, ID=cancel_reservation_request.reservation_id)

        return self.client.service.cancelReservation(
            Version=cancel_reservation_request.version,
            SequenceNmbr=cancel_reservation_request.sequenceNmbr,
            POS=pos,
            Reservation={"UniqueID": [uniqueID], "CancelType": xsd.SkipValue},
        )

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

    def __init__(self):
        self.session = self._create_wsdl_session()
