from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from django.http import HttpResponse
from zeep import helpers
import json
import decimal

from api.carey.carey_service import CareyService
from api.carey.carey_search import CareySearch
from api.common.common_models import from_json

from api.carey.models.carey_api_model import (
    RateInquiryRequest,
    BookReservationRequest,
    FindReservationRequest,
    CancelReservationRequest,
)
from api.carey.parsers.carey_parser import CareyParser
from api.view.default_view import _response

carey_service = CareyService()
carey_search = CareySearch()


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        # Provide a fallback to the default encoder if we haven't implemented special support for the object's class
        return super(DecimalEncoder, self).default(o)


class CareyViewSet(viewsets.ViewSet):
    @action(detail=False, url_path="rate-inqury", methods=["POST"], name="Get quotes for a journey")
    def get_rate_inquiry(self, request: Request):
        rate_inquiry_request = from_json(request.data, RateInquiryRequest)
        quote_response = carey_service.get_quote_inquiry(rate_inquiry_request)
        if quote_response["Errors"]:
            jsondata = helpers.serialize_object(quote_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            jsondata = helpers.serialize_object(quote_response["GroundServices"])
            parse_quote_data = CareyParser()
            quote_data = list(
                parse_quote_data.parse_quotes(quote_response["GroundServices"]["GroundService"], rate_inquiry_request)
            )
            return _response(quote_data)

    @action(detail=False, url_path="book-reservation", methods=["POST"], name="Book a reservation")
    def get_add_reservation(self, request: Request):
        book_reservation_request = from_json(request.data, BookReservationRequest)
        book_response = carey_service.get_book_reservation(book_reservation_request)
        print("book_response===================", book_response)
        if book_response["Errors"]:
            jsondata = helpers.serialize_object(book_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            parse_quote_data = CareyParser()
            response_data = parse_quote_data.parse_booking_response(book_response)
            return _response(response_data)

    @action(detail=False, url_path="find-reservation", methods=["POST"], name="Find a reservation")
    def get_find_reservation(self, request: Request):
        find_reservation_request = from_json(request.data, FindReservationRequest)
        find_response = carey_service.get_find_reservation(find_reservation_request)
        if find_response["Errors"]:
            jsondata = helpers.serialize_object(find_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            parse_quote_data = CareyParser()
            response_data = parse_quote_data.parse_find_response(find_response)
            return _response(response_data)

    @action(detail=False, url_path="cancel-reservation", methods=["POST"], name="Cancel a reservation")
    def get_cancel_reservation(self, request: Request):
        cancel_reservation_request = from_json(request.data, CancelReservationRequest)
        cancel_response = carey_service.get_cancel_reservation(cancel_reservation_request)
        if cancel_response["Errors"]:
            jsondata = helpers.serialize_object(cancel_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            parse_quote_data = CareyParser()
            response_data = parse_quote_data.parse_cancel_response(cancel_response)
            return _response(response_data)
