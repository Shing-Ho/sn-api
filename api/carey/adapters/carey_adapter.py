import warnings
import requests
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
        endpoint = "https://api.carey.com:8443/sandbox/CSIOTAProxy_v2/CareyReservationService"
        pickupdate = book_reservation_request.quoteInfo.pickUpDate
        pickupLocation = book_reservation_request.quoteInfo.pickUpLoacation
        dropoffLocation = book_reservation_request.quoteInfo.dropOffLocation
        pickLat = pickupLocation.latitude
        pickLnt = pickupLocation.longitude
        pickLocationName = pickupLocation.locationName
        pickAddressline = pickupLocation.addressLine
        pickCityName = pickupLocation.cityName
        pickPostalCode = pickupLocation.postalCode
        pickStateCode = pickupLocation.stateProv.stateCode
        pickStateProv = pickupLocation.stateProv.value
        pickCountryCode = pickupLocation.countryName.stateCode
        pickCountryName = pickupLocation.countryName.value
        dropLocationName = dropoffLocation.locationName
        dropAirportCode = dropoffLocation.airportCode
        givenName = book_reservation_request.passengerInfo.firstName
        surName = book_reservation_request.passengerInfo.lastName
        phoneNum = book_reservation_request.passengerInfo.phoneNum
        email = book_reservation_request.passengerInfo.email
        maxPassenger = book_reservation_request.quoteInfo.passengers
        maxBaggage = book_reservation_request.quoteInfo.bags
        vehicleCode = book_reservation_request.quoteInfo.vehicleDetails.vehicleCode
        vehicleName = book_reservation_request.quoteInfo.vehicleDetails.vehicleName
        special = book_reservation_request.quoteInfo.special
        paymentInfo = book_reservation_request.paymentInfo
        billingAddress = paymentInfo.billingAddress
        expDate = paymentInfo.expDate
        cardType = paymentInfo.cardType
        cardName = paymentInfo.cardName
        billAddressline = billingAddress.addressLine
        billCityName = billingAddress.cityName
        billPostalCode = billingAddress.postalCode
        billStateCode = billingAddress.stateProv.stateCode
        billStateProv = billingAddress.stateProv.value
        billCountryCode = billingAddress.countryName.stateCode
        billCountryName = billingAddress.countryName.value
        cardToken = paymentInfo.expCVV
        cardNum = paymentInfo.cardNum
        # noqa: E501
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ns="http://www.opentravel.org/OTA/2003/05">
            <soapenv:Header/>
            <soapenv:Body>
                <ns:OTA_GroundBookRQ EchoToken="1" TimeStamp="2020-12-12T03:41:00" SequenceNmbr="27">
                    <ns:POS>
                        <ns:Source>
                            <ns:RequestorID
                            MessagePassword="carey123"
                            Type="TA"
                            ID="testarranger@testnone.com"></ns:RequestorID>
                            <ns:BookingChannel>
                                <ns:CompanyName Code=""
                                CodeContext="52969"
                                CompanyShortName="PM744">CSI - SimpleNight</ns:CompanyName>
                            </ns:BookingChannel>
                        </ns:Source>
                    </ns:POS>
                    <ns:Reference>
                        <ns:TPA_Extensions>
                            <ns:PNRNumber/>
                            <ns:SpecialQuotes/>
                            <ns:IsGuestBooking>false</ns:IsGuestBooking>
                            <ns:IsDropOffTripDuration>false</ns:IsDropOffTripDuration>
                            <ns:IsNextDay>false</ns:IsNextDay>
                        </ns:TPA_Extensions>
                    </ns:Reference>
                    <ns:GroundReservation>
                        <ns:Location>
                            <ns:Pickup DateTime="{pickupdate}">
                                <ns:Address Latitude="{pickLat}" Longitude="{pickLnt}">
                                    <ns:LocationName>{pickLocationName}</ns:LocationName>
                                    <ns:AddressLine>{pickAddressline}</ns:AddressLine>
                                    <ns:CityName>{pickCityName}</ns:CityName>
                                    <ns:PostalCode>{pickPostalCode}</ns:PostalCode>
                                    <ns:StateProv Code="{pickStateCode}">{pickStateProv}</ns:StateProv>
                                    <ns:CountryName Code="{pickCountryCode}">{pickCountryName}</ns:CountryName>
                                </ns:Address>
                            </ns:Pickup>
                            <ns:Dropoff>
                                <ns:AirportInfo>
                                    <ns:Departure AirportName="" LocationCode="{dropAirportCode}"></ns:Departure>
                                </ns:AirportInfo>
                                <ns:Airline FlightDateTime="" FlightNumber="" Code=""></ns:Airline>
                            </ns:Dropoff>
                        </ns:Location>
                        <ns:Passenger>
                            <ns:Primary>
                                <ns:PersonName>
                                    <ns:GivenName>{givenName}</ns:GivenName>
                                    <ns:Surname>{surName}</ns:Surname>
                                </ns:PersonName>
                                <ns:Telephone PhoneNumber="{phoneNum}"
                                 PhoneUseType="1"
                                 CountryAccessCode="1"></ns:Telephone>
                                <ns:Email>{email}</ns:Email>
                            </ns:Primary>
                        </ns:Passenger>
                        <ns:Service DisabilityVehicleInd="false"
                            MaximumPassengers="{maxPassenger}"
                            MaximumBaggage="{maxBaggage}"
                            GreetingSignInd="false">
                            <ns:ServiceLevel Code="Point-To-Point" Description="Premium"></ns:ServiceLevel>
                            <ns:VehicleType Code="ES03">{vehicleName}</ns:VehicleType>
                        </ns:Service>
                        <ns:Payments>
                            <ns:Payment PaymentTransactionTypeCode="ByPaymentCC">
                                <ns:PaymentCard ExpireDate="03/21">
                                    <ns:CardType Code="VISA"></ns:CardType>
                                    <ns:CardHolderName>Name1 Surname1</ns:CardHolderName>
                                    <ns:Address>
                                        <ns:AddressLine>Address Line 1</ns:AddressLine>
                                        <ns:CityName>City Name</ns:CityName>
                                        <ns:PostalCode>12345</ns:PostalCode>
                                        <ns:StateProv StateCode="WA">Washington</ns:StateProv>
                                        <ns:CountryName Code="US">United States</ns:CountryName>
                                    </ns:Address>
                                    <ns:CardNumber Token="111">
                                        <ns:PlainText>4333333333333339</ns:PlainText>
                                    </ns:CardNumber>
                                </ns:PaymentCard>
                            </ns:Payment>
                        </ns:Payments>
                    </ns:GroundReservation>
                    <ns:TPA_Extensions>
                        <ns:PickUpSpecialInstructions>{special}</ns:PickUpSpecialInstructions>
                    </ns:TPA_Extensions>
                </ns:OTA_GroundBookRQ>
            </soapenv:Body>
        </soapenv:Envelope>""".format(
            pickupdate=pickupdate,
            pickLat=pickLat,
            pickLnt=pickLnt,
            pickLocationName=pickLocationName,
            pickAddressline=pickAddressline,
            pickCityName=pickCityName,
            pickPostalCode=pickPostalCode,
            pickStateCode=pickStateCode,
            pickCountryCode=pickCountryCode,
            pickStateProv=pickStateProv,
            pickCountryName=pickCountryName,
            dropLocationName=dropLocationName,
            dropAirportCode=dropAirportCode,
            givenName=givenName,
            surName=surName,
            phoneNum=phoneNum,
            email=email,
            maxPassenger=maxPassenger,
            maxBaggage=maxBaggage,
            vehicleCode=vehicleCode,
            vehicleName=vehicleName,
            special=special,
            expDate=expDate,
            cardType=cardType,
            cardName=cardName,
            billAddressline=billAddressline,
            billCityName=billCityName,
            billPostalCode=billPostalCode,
            billStateCode=billStateCode,
            billStateProv=billStateProv,
            billCountryCode=billCountryCode,
            billCountryName=billCountryName,
            cardToken=cardToken,
            cardNum=cardNum,
        )
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "X-SOAP-Method": "addReservation",
            "app_id": "2b58cb23",
            "app_key": "1c21f0a1e3f860f5353d863ca75b0138",
        }
        r = requests.post(endpoint, data=body, headers=headers)
        return r.text

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
            SequenceNmbr=200050,
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
