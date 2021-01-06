from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from django.http import HttpResponse
import json

from api.charging.charging_service import ChargingService


class ChargingViewSet(viewsets.ViewSet):
    @action(detail=False, url_path="poi", methods=["GET"], name="Search charging location")
    def get_poi(self, request: Request):
        charging = ChargingService()
        poi = charging.get_poi(request)
        filteredResponse = list(map((lambda x: {
            "ID": x["ID"],
            "UUID": x["UUID"],
            "UserComments": x["UserComments"],
            "MediaItems": x["MediaItems"],
            "UsageType": x["UsageType"],
            "StatusType": x["StatusType"],
            "UsageCost": x["UsageCost"],
            "AddressInfo": x["AddressInfo"],
            "NumberOfPoints": x["NumberOfPoints"],
            "GeneralComments": x["GeneralComments"],
            "Connections": x["Connections"],
        }), poi.json()))
        return HttpResponse(json.dumps(filteredResponse), content_type="application/json")

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
