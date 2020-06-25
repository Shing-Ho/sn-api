import json

from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from uszipcode import SearchEngine

from api.models.models import Geoname, GeonameAlternateName, mappingcodes
from . import serializers
from .hotel.hotels import HotelSearchRequest
from .hotel.travelport import TravelportHotelAdapter
from .permissions import TokenAuthSupportQueryString
from .serializers import LocationsSerializer, HotelAdapterHotelSerializer, mappingcodesSerializer

data = open("airports.json", encoding="utf-8").read()
location_dictionary = json.loads(data)


def location_formater(request):
    city = request.GET.get("city")
    search = SearchEngine()

    if city:
        city_name = search.by_city(city=city, sort_by="population", returns=10)[
            0].major_city
        return HttpResponse(json.dumps({city_name: location_dictionary[city_name]["iata"]}))


class HotelBedsMap(viewsets.ModelViewSet):
    queryset = mappingcodes.objects.all()
    serializer_class = mappingcodesSerializer

    def get_queryset(self):
        queryset = self.queryset
        city = self.request.GET.get("city")
        provider_id = self.request.GET.get("provider_id")
        hotel_codes = self.request.GET.get("hotel_codes")
        hotel_name = self.request.GET.get("hotel_name")
        rating = self.request.GET.get("rating")
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
        return queryset


def index(request):
    return HttpResponse("Hello, World!  This is the index page")


class HotelSupplierViewset(viewsets.ViewSet):
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (IsAuthenticated,)
    serializer_class = (HotelAdapterHotelSerializer,)
    hotel_adapter = TravelportHotelAdapter()

    @action(detail=False, methods=["GET"], name="Search Hotels")
    def search(self, request):
        location = request.GET.get("location")
        checkin = request.GET.get("checkin")
        checkout = request.GET.get("checkout")
        num_adults = request.GET.get("num_adults")
        ratetype = request.GET.get("ratetype")
        snpropertyid = request.GET.get("snpropertyid")
        language = request.GET.get("language")
        hotels = self.hotel_adapter.search(
            HotelSearchRequest(location, checkin, checkout, ratetype,
                               language, snpropertyid, num_adults=num_adults)
        )
        serializer = serializers.HotelAdapterHotelSerializer(
            instance=hotels, many=True)

        return Response(serializer.data)


class LocationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geoname.objects.all()
    serializer_class = LocationsSerializer
    authentication_classes = (TokenAuthSupportQueryString,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        lang_code = self.request.GET.get("lang_code", "en")
        country = self.request.GET.get("country")

        if lang_code.lower() != "all":
            lang_filter = GeonameAlternateName.objects.filter(
                iso_language_code=lang_code)
            queryset = queryset.prefetch_related(Prefetch("lang", lang_filter))
            queryset = queryset.filter(lang__iso_language_code=lang_code)
        else:
            queryset = queryset.prefetch_related("lang")

        if country:
            queryset = queryset.filter(iso_country_code=country)

        return queryset
