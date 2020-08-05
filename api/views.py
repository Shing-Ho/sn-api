import json

import stripe
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from uszipcode import SearchEngine

from api.models.models import supplier_hotels
from . import api_access
from .api_access import ApiAccessRequest
from .common.models import to_json
from .serializers import mappingcodesSerializer

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
data = open("airports.json", encoding="utf-8").read()
location_dictionary = json.loads(data)


def index(request):
    return HttpResponse(status=404)


def location_formater(request):
    city = request.GET.get("city")
    search = SearchEngine()

    if city:
        city_name = search.by_city(city=city, sort_by="population", returns=10)[0].major_city
        return HttpResponse(json.dumps({city_name: location_dictionary[city_name]["iata"]}))


class HotelBedsMap(viewsets.ModelViewSet):
    queryset = supplier_hotels.objects.all()
    serializer_class = mappingcodesSerializer

    def get_queryset(self):
        queryset = self.queryset
        city = self.request.GET.get("city")
        provider_id = self.request.GET.get("provider_id")
        hotel_codes = self.request.GET.get("hotel_codes")
        category_name = self.request.GET.get("category_name")
        chain_name = self.request.GET.get("chain_name")
        country_name = self.request.GET.get("country_name")
        destination_name = self.request.GET.get("destination_name")
        address = self.request.GET.get("address")
        postal_code = self.request.GET.get("postal_code")
        latitude = self.request.GET.get("latitude")
        longitude = self.request.GET.get("longitude")

        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        if hotel_codes:
            queryset = queryset.filter(hotel_codes=hotel_codes)
        if category_name:
            queryset = queryset.filter(rating=category_name)
        if chain_name:
            queryset = queryset.filter(chain_name=chain_name)
        if country_name:
            queryset = queryset.filter(country_name=country_name)
        if destination_name:
            queryset = queryset.filter(destination_name=destination_name)
        if address:
            queryset = queryset.fiter(address__isin=address)
        if postal_code:
            queryset = queryset.filter(postal_code=postal_code)
        if city:
            queryset = queryset.filter(city=city)
        if latitude:
            queryset = queryset.filter(latitude=latitude)
        if longitude:
            queryset = queryset.filter(longitude=longitude)
            # hotels beds id - - > sn_id - 4
            # other provider ids > send provider id to corresponding provider
            # -- get data back and display what we want to users
        return queryset


class AuthenticationView(viewsets.ViewSet):
    @action(detail=False, methods=["POST"], name="Create Anonymous API Key")
    def create_api_key(self, request):
        request = ApiAccessRequest.Schema().load(request.data)
        if not request:
            return Response(status=400)

        response = api_access.create_anonymous_api_user(request)
        return _response(response)


def _response(obj):
    return Response(to_json(obj))
