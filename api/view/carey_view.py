from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from django.http import HttpResponse

from api.carey.carey_service import CareyService

carey_service = CareyService()


class CareyViewSet(viewsets.ViewSet):
    @action(detail=False, url_path="rate-inqury", methods=["POST"], name="Get quotes for a journey")
    def request_quote_inquiry(self, request: Request):
        response = carey_service.request_quote_inquiry(request)
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="book-reservation", methods=["POST"], name="Get reference data")
    def request_book_reservation(self, request: Request):
        response = carey_service.request_book_reservation(request)
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="find-reservation", methods=["POST"], name="Get reference data")
    def find_reservation(self, request: Request):
        response = carey_service.find_reservation(request)
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="cancel-reservation", methods=["POST"], name="Get reference data")
    def cancel_reservation(self, request: Request):
        response = carey_service.cancel_reservation(request)
        return HttpResponse(response, content_type="application/json")

    @action(detail=False, url_path="modify-reservation", methods=["POST"], name="Get reference data")
    def modify_reservation(self, request: Request):
        response = carey_service.modify_reservation(request)
        return HttpResponse(response, content_type="application/json")
