from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.models import Hotels, Geoname, GeonameAlternateName
from . import serializers
from .hotel.hotels import HotelSearchRequest
from api.hotel.travelport.travelport import TravelportHotelAdapter
from .permissions import TokenAuthSupportQueryString
from .serializers import (
    HotelsSerializer,
    LocationsSerializer,
    HotelAdapterHotelSerializer,
)


def index(request):
    return HttpResponse("Hello, World!  This is the index page")


def detail(request):

    return HttpResponse("there are currently {} Hotelss in the Hotels model".format(Hotels.objects.all().count()))


class HotelsViewset(viewsets.ModelViewSet):
    queryset = Hotels.objects.all()
    serializer_class = HotelsSerializer

    def get_queryset(self):
        queryset = self.queryset
        locations = self.request.GET.get("locations")
        minstars = self.request.GET.get("minstars")
        if locations:
            queryset = queryset.filter(city=locations)
        if minstars:
            queryset = queryset.filter(stars__gt=minstars)
        return queryset


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

        hotels = self.hotel_adapter.search(HotelSearchRequest(location, checkin, checkout, num_adults=num_adults))
        serializer = serializers.HotelAdapterHotelSerializer(instance=hotels, many=True)

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
            lang_filter = GeonameAlternateName.objects.filter(iso_language_code=lang_code)
            queryset = queryset.prefetch_related(Prefetch("lang", lang_filter))
            queryset = queryset.filter(lang__iso_language_code=lang_code)
        else:
            queryset = queryset.prefetch_related("lang")

        if country:
            queryset = queryset.filter(iso_country_code=country)

        return queryset
