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

from api.carey.models.carey_api_model import RateInquiryRequest

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
        _response = carey_service.get_quote_inquiry(rate_inquiry_request)
        if _response["Errors"]:
            jsondata = helpers.serialize_object(_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            jsondata = helpers.serialize_object(_response["GroundServices"])
            response = json.dumps(jsondata, cls=DecimalEncoder)
            return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="book-reservation", methods=["POST"], name="Book a reservation")
    def get_add_reservation(self, request: Request):
        _response = carey_service.get_book_reservation(request.data)
        if _response["Errors"]:
            jsondata = helpers.serialize_object(_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            jsondata = helpers.serialize_object(_response)
            response = json.dumps(jsondata, cls=DecimalEncoder)
            return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="modify-reservation", methods=["POST"], name="Modify a reservation")
    def get_modify_reservation(self, request: Request):
        _response = carey_service.get_modify_reservation(request.data)
        if _response["Errors"]:
            jsondata = helpers.serialize_object(_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            jsondata = helpers.serialize_object(_response)
            response = json.dumps(jsondata, cls=DecimalEncoder)
            return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="find-reservation", methods=["POST"], name="Find a reservation")
    def get_find_reservation(self, request: Request):
        _response = carey_service.get_find_reservation(request.data)
        if _response["Errors"]:
            jsondata = helpers.serialize_object(_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            jsondata = helpers.serialize_object(_response)
            response = json.dumps(jsondata, cls=DecimalEncoder)
            return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="cancel-reservation", methods=["POST"], name="Cancel a reservation")
    def get_cancel_reservation(self, request: Request):
        _response = carey_service.get_cancel_reservation(request.data)
        if _response["Errors"]:
            jsondata = helpers.serialize_object(_response["Errors"]["Error"][0]["_value_1"])
            error_message = {"message": jsondata}
            return HttpResponse(json.dumps(error_message), content_type="application/json", status=404)
        else:
            jsondata = helpers.serialize_object(_response)
            response = json.dumps(jsondata, cls=DecimalEncoder)
            return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="search-reservation", methods=["POST"], name="Search a reservation")
    def search_reservation(self, request: Request):
        response = carey_search.search_reservation(request)
        return HttpResponse(response, content_type="application/json")
