from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from django.http import HttpResponse

from api.charging.charging_service import ChargingService


class ChargingViewSet(viewsets.ViewSet):
    @action(detail=False, url_path="poi", methods=["GET"], name="Search charging location")
    def get_poi(self, request: Request):
        charging = ChargingService()
        poi = charging.get_poi(request)
        return HttpResponse(poi, content_type="application/json")

    @action(detail=False, url_path="referencedata", methods=["GET"], name="Get reference data")
    def get_reference(self, request: Request):
        charging = ChargingService()
        reference = charging.get_reference(request)
        return HttpResponse(reference, content_type="application/json")

    @action(detail=False, url_path="comment", methods=["POST"], name="Post comment")
    def post_comment(self, request: Request):
        charging = ChargingService()
        response = charging.post_comment(request)
        return HttpResponse(response, content_type="application/json")
