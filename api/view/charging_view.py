from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from django.http import HttpResponse

from api.charging.charging_service import ChargingService


class ChargingViewSet(viewsets.ViewSet):
    @action(detail=False, url_path="poi", methods=["GET"], name="Search charging location")
    def get_all(self, request: Request):
        charging = ChargingService()
        poi = charging.get_poi(request)
        return HttpResponse(poi, content_type="application/json")
