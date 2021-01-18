from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from django.http import HttpResponse
import json

from api.carey.carey_service import CareyService

carey_service = CareyService()


class CareyViewSet(viewsets.ViewSet):
    @action(detail=False, url_path="rate-inqury", methods=["POST"], name="Get quotes for a journey")
    def get_rate_inquiry(self, request: Request):
        _response = carey_service.get_quote_inquiry(request)
        response = json.loads(json.dumps(_response, default=str))
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="book-reservation", methods=["POST"], name="Book a reservation")
    def get_add_reservation(self, request: Request):
        _response = carey_service.get_book_reservation(request)
        response = json.loads(json.dumps(_response, default=str))
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="modify-reservation", methods=["POST"], name="Modify a reservation")
    def get_modify_reservation(self, request: Request):
        _response = carey_service.get_modify_reservation(request)
        response = json.loads(json.dumps(_response, default=str))
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="find-reservation", methods=["POST"], name="Find a reservation")
    def get_find_reservation(self, request: Request):
        _response = carey_service.get_find_reservation(request)
        response = json.loads(json.dumps(_response, default=str))
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="cancel-reservation", methods=["POST"], name="Cancel a reservation")
    def get_cancel_reservation(self, request: Request):
        _response = carey_service.get_cancel_reservation(request)
        response = json.loads(json.dumps(_response, default=str))
        return HttpResponse(response, content_type="application/json")
