from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models.models import hotel_listing
from . import api_access
from .api_access import ApiAccessRequest
from .common.models import to_json
from .serializers import HotelListingSerializer


class HotellistView(viewsets.ModelViewSet):
    queryset = hotel_listing.objects.all()
    serializer_class = HotelListingSerializer

    def get_queryset(self):

        queryset = self.queryset
        snid = self.request.GET.get("snid")

        if snid:
            queryset = queryset.filter(simplenight_id=snid)

        return queryset


def index(request):
    return HttpResponse(status=404)


class AuthenticationView(viewsets.ViewSet):
    @action(detail=False, methods=["POST"], name="Create Anonymous API Key")
    def create_api_key(self, request):
        request = ApiAccessRequest.Schema().load(request.data)
        if not request:
            return Response(status=400)

        response = api_access.create_anonymous_api_user(request)
        return _response(response)


def _response(obj):
    return Response(to_json(obj), content_type="application/json")
