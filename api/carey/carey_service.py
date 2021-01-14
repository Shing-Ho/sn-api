import requests
import json
import xmltodict

from api.carey.settings import CONFIG


class CareyService:
    def __init__(self):
        self.config = CONFIG
        self.app_id = self.config["app_id"]
        self.app_key = self.config["app_key"]

    def generate_header(self):
        return {
            "Content-Type": "text/xml",
            "api_-id": self.app_id,
            "x-api-key": self.app_key,
        }

    def get_wsdl_url(self):
        return "https://sandbox.carey.com/CSIOTAProxy_v2/CareyReservationService?wsdl"

    def request_quote_inquiry(self, request):
        url = self.get_wsdl_url()
        headers = self.generate_header()
        body = """<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.opentravel.org/OTA/2003/05\">\r\n<soapenv:Header/>\r\n<soapenv:Body>\r\n<ns:OTA_GroundAvailRQ TimeStamp=\"2017-12-12T03:41:00\" >\r\n<ns:POS>\r\n<ns:Source>\r\n<ns:RequestorID/>\r\n<ns:BookingChannel>\r\n<ns:CompanyName Code=\"\" CodeContext=\"52969\" CompanyShortName=\"PM744\">CSI - SimpleNight</ns:CompanyName>\r\n</ns:BookingChannel>\r\n</ns:Source>\r\n</ns:POS>\r\n<ns:Service>\r\n<ns:Pickup DateTime=\"2021-02-06T15:00:00\">\r\n<ns:Address Latitude=\"\" Longitude=\"\">\r\n<ns:LocationName>Four Seasons Hotel Seattle</ns:LocationName>\r\n\t<ns:AddressLine>99 Union Street</ns:AddressLine>\r\n<ns:CityName>Seattle</ns:CityName>\r\n\t<ns:PostalCode>98101</ns:PostalCode>\r\n<ns:StateName StateCode=\"WA\">Washington</ns:StateName>\r\n<ns:CountryName Code=\"US\">United States</ns:CountryName>\r\n\t\t</ns:Address>\r\n</ns:Pickup>\r\n<ns:Dropoff>\r\n<ns:AirportInfo>\r\n<ns:Departure AirportName=\"\" LocationCode=\"SEA\"></ns:Departure>\r\n</ns:AirportInfo>\r\n<ns:Airline FlightDateTime=\"\" FlightNumber=\"\" Code=\"\"></ns:Airline>\r\n</ns:Dropoff>\r\n</ns:Service>\r\n<ns:ServiceType Code=\"Point-To-Point\" Description=\"ALL\"></ns:ServiceType>\r\n<ns:PassengerPrefs MaximumBaggage=\"1\" MaximumPassengers=\"1\" GreetingSignInd=\"false\"></ns:PassengerPrefs>\r\n<ns:RateQualifier AccountId=\"\"></ns:RateQualifier>\r\n</ns:OTA_GroundAvailRQ>\r\n</soapenv:Body>\r\n</soapenv:Envelope>"""  # noqa: E501

        response = requests.post(url, data=body, headers=headers)
        json_results = json.dumps(xmltodict.parse(response.content))
        return json_results

    def request_book_reservation(self, request):
        url = self.get_wsdl_url()
        headers = self.generate_header()
        body = """<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.opentravel.org/OTA/2003/05\">\r\n<soapenv:Header/>\r\n<soapenv:Body>\r\n<ns:OTA_GroundBookRQ EchoToken=\"1\" TimeStamp=\"2020-12-12T03:41:00\" SequenceNmbr=\"200004\">\r\n<ns:POS>\r\n<ns:Source>\r\n<ns:RequestorID MessagePassword=\"carey123\" Type=\"TA\" ID=\"testarranger@testnone.com\"></ns:RequestorID>\r\n<ns:BookingChannel>\r\n<ns:CompanyName Code=\"\" CodeContext=\"52969\" CompanyShortName=\"PM744\">CSI - SimpleNight</ns:CompanyName>\r\n</ns:BookingChannel>\r\n</ns:Source>\r\n</ns:POS>\r\n<ns:Reference>\r\n<ns:TPA_Extensions>\r\n<ns:PNRNumber/>\r\n<ns:SpecialQuotes/>\r\n<ns:IsGuestBooking>false</ns:IsGuestBooking>\r\n<ns:IsDropOffTripDuration>false</ns:IsDropOffTripDuration>\r\n<ns:IsNextDay>false</ns:IsNextDay>\r\n</ns:TPA_Extensions>\r\n</ns:Reference>\r\n<ns:GroundReservation>\r\n<ns:Location>\r\n<ns:Pickup DateTime=\"2021-02-06T15:00:00\">\r\n<ns:Address Latitude=\"\" Longitude=\"\">\r\n<ns:LocationName>Four Seasons Hotel Seattle</ns:LocationName>\r\n\t<ns:AddressLine>99 Union Street</ns:AddressLine>\r\n<ns:CityName>Seattle</ns:CityName>\r\n\t<ns:PostalCode>98101</ns:PostalCode>\r\n<ns:StateName StateCode=\"WA\">Washington</ns:StateName>\r\n<ns:CountryName Code=\"US\">United States</ns:CountryName>\r\n\t\t</ns:Address>\r\n</ns:Pickup>\r\n<ns:Dropoff>\r\n<ns:AirportInfo>\r\n<ns:Departure AirportName=\"\" LocationCode=\"SEA\"></ns:Departure>\r\n</ns:AirportInfo>\r\n<ns:Airline FlightDateTime=\"\" FlightNumber=\"\" Code=\"\"></ns:Airline>\r\n</ns:Dropoff>\r\n</ns:Location>\r\n<ns:Passenger>\r\n<ns:Primary>\r\n<ns:PersonName>\r\n<ns:GivenName>TestPax</ns:GivenName>\r\n<ns:Surname>TestPax</ns:Surname>\r\n</ns:PersonName>\r\n<ns:Telephone PhoneNumber=\"1111111111\" PhoneUseType=\"1\" CountryAccessCode=\"1\"></ns:Telephone>\r\n<ns:Email>testpassenger@testnone.com</ns:Email>\r\n</ns:Primary>\r\n</ns:Passenger>\r\n<ns:Service DisabilityVehicleInd=\"false\"  MaximumPassengers=\"1\" MaximumBaggage=\"1\" GreetingSignInd=\"false\">\r\n<ns:ServiceLevel Code=\"Point-To-Point\" Description=\"Premium\"></ns:ServiceLevel>\r\n<ns:VehicleType Code=\"ES03\">Executive Sedan</ns:VehicleType>\r\n</ns:Service>\r\n<ns:Payments>\r\n\t\t\t\t\t<ns:Payment PaymentTransactionTypeCode=\"ByPaymentCC\">\r\n\t\t\t\t\t\t<ns:PaymentCard ExpireDate=\"03/21\">\r\n\t\t\t\t\t\t\t<ns:CardType Code=\"VISA\"></ns:CardType>\r\n\t\t\t\t\t\t\t<ns:CardHolderName>Name1 Surname1</ns:CardHolderName>\r\n\t\t\t\t\t\t\t<ns:Address>\r\n\t\t\t\t\t\t\t\t<ns:AddressLine>Address Line 1</ns:AddressLine>\r\n\t\t\t\t\t\t\t\t<ns:CityName>City Name</ns:CityName>\r\n\t\t\t\t\t\t\t\t<ns:PostalCode>12345</ns:PostalCode>\r\n\t\t\t\t\t\t\t\t<ns:StateProv StateCode=\"WA\">Washington</ns:StateProv>\r\n\t\t\t\t\t\t\t\t<ns:CountryName Code=\"US\">United States</ns:CountryName>\r\n\t\t\t\t\t\t\t</ns:Address>\r\n\t\t\t\t\t\t\t<ns:CardNumber Token=\"111\">\r\n\t\t\t\t\t\t\t\t<ns:PlainText>4333333333333339</ns:PlainText>\r\n\t\t\t\t\t\t\t</ns:CardNumber>\r\n\t\t\t\t\t\t</ns:PaymentCard>\r\n\t\t\t\t\t</ns:Payment>\r\n\t\t\t\t</ns:Payments>\r\n</ns:GroundReservation>\r\n<ns:TPA_Extensions>\r\n<ns:PickUpSpecialInstructions>Test special instructions</ns:PickUpSpecialInstructions>\r\n</ns:TPA_Extensions>\r\n</ns:OTA_GroundBookRQ>\r\n</soapenv:Body>\r\n</soapenv:Envelope>"""  # noqa: E501

        response = requests.post(url, data=body, headers=headers)
        json_results = json.dumps(xmltodict.parse(response.content))
        return json_results

    def find_reservation(self, request):
        url = self.get_wsdl_url()
        headers = self.generate_header()
        body = """<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.opentravel.org/OTA/2003/05\">\r\n<soapenv:Header/>\r\n<soapenv:Body>\r\n<ns:OTA_GroundResRetrieveRQ TimeStamp=\"2017-12-12T05:43:21.960-04:00\">\r\n<ns:POS>\r\n<ns:Source>\r\n<ns:BookingChannel>\r\n<ns:CompanyName Code=\"\" CodeContext=\"52969\" CompanyShortName=\"PM744\">CSI - SimpleNight</ns:CompanyName>\r\n</ns:BookingChannel>\r\n</ns:Source>\r\n</ns:POS>\r\n<ns:Reference ID=\"WA13193419-1\"/>\r\n</ns:OTA_GroundResRetrieveRQ>\r\n</soapenv:Body>\r\n</soapenv:Envelope>"""  # noqa: E501

        response = requests.post(url, data=body, headers=headers)
        json_results = json.dumps(xmltodict.parse(response.content))
        return json_results

    def cancel_reservation(self, request):
        url = self.get_wsdl_url()
        headers = self.generate_header()
        body = """<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.opentravel.org/OTA/2003/05\">\r\n<soapenv:Header/>\r\n<soapenv:Body>\r\n<ns:OTA_GroundCancelRQ TimeStamp=\"2020-12-12T03:41:00\" EchoToken=\"1\" SequenceNmbr=\"200007\" Version=\"2\">\r\n<ns:POS>\r\n<ns:Source>\r\n<ns:RequestorID ID=\"testarranger@testnone.com\" MessagePassword=\"carey123\" Type=\"TA\"/>\r\n<ns:BookingChannel Type=\"TA\">\r\n<ns:CompanyName Code=\"\" CodeContext=\"52969\" CompanyShortName=\"PM744\">CSI - SimpleNight</ns:CompanyName>\r\n</ns:BookingChannel>\r\n</ns:Source>\r\n</ns:POS>\r\n<ns:Reservation>\r\n    <ns:UniqueID ID=\"WA13193419-1\"/>\r\n</ns:Reservation>\r\n</ns:OTA_GroundCancelRQ>\r\n</soapenv:Body>\r\n</soapenv:Envelope>"""  # noqa: E501

        response = requests.post(url, data=body, headers=headers)
        json_results = json.dumps(xmltodict.parse(response.content))
        return json_results

    def modify_reservation(self, request):
        url = self.get_wsdl_url()
        headers = self.generate_header()
        body = """<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.opentravel.org/OTA/2003/05\">\r\n<soapenv:Header/>\r\n<soapenv:Body>\r\n<ns:OTA_GroundResRetrieveRQ TimeStamp=\"2017-12-12T05:43:21.960-04:00\">\r\n<ns:POS>\r\n<ns:Source>\r\n<ns:BookingChannel>\r\n<ns:CompanyName Code=\"\" CodeContext=\"52969\" CompanyShortName=\"PM744\">CSI - SimpleNight</ns:CompanyName>\r\n</ns:BookingChannel>\r\n</ns:Source>\r\n</ns:POS>\r\n<ns:Reference ID=\"WA13193419-1\"/>\r\n</ns:OTA_GroundResRetrieveRQ>\r\n</soapenv:Body>\r\n</soapenv:Envelope>"""  # noqa: E501

        response = requests.post(url, data=body, headers=headers)
        json_results = json.dumps(xmltodict.parse(response.content))
        return json_results
