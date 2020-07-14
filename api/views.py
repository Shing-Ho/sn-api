import json
from datetime import date

from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from uszipcode import SearchEngine

from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.models.models import Geoname, GeonameAlternateName
from api.models.models import supplier_hotels
from . import serializers, api_access
from .api_access import ApiAccessRequest, ApiAccessResponse
from .auth.models import HasOrganizationAPIKey, OrganizationApiThrottle
from .hotel.adapters.hotel_service import HotelService
from .hotel.hotels import (
    HotelLocationSearch,
    HotelSpecificSearch,
    RoomOccupancy,
    HotelSearchResponse,
    HotelBookingRequest,
    HotelBookingResponse,
)
from .serializers import (
    LocationsSerializer,
    HotelAdapterHotelSerializer,
)
from .serializers import mappingcodesSerializer

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
            # hotels beds id - - > sn_id - 4
            # other provider ids > send provider id to corresponding provider
            # -- get data back and display what we want to users
        return queryset


class HotelSupplierViewset(viewsets.ViewSet):
    permission_classes = (HasOrganizationAPIKey,)
    throttle_classes = (OrganizationApiThrottle,)
    serializer_class = (HotelAdapterHotelSerializer,)
    hotel_adapter = TravelportHotelAdapter()
    hotel_service = HotelService("stub")

    @action(detail=False, methods=["GET"], name="Search Hotels")
    def search_by_location(self, request):
        location = request.GET.get("location")
        checkin = request.GET.get("checkin")
        checkout = request.GET.get("checkout")
        num_adults = request.GET.get("num_adults")
        hotels = self.hotel_adapter.search_by_location(
            HotelLocationSearch(
                location_name=location,
                checkin_date=checkin,
                checkout_date=checkout,
                occupancy=RoomOccupancy(adults=num_adults),
            )
        )

        serializer = serializers.HotelAdapterHotelSerializer(instance=hotels, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["GET"], name="Search Hotels")
    def search_by_id(self, request):
        hotel_code = request.GET.get("hotel_code")
        checkin = date.fromisoformat(request.GET.get("checkin"))
        checkout = date.fromisoformat(request.GET.get("checkout"))
        num_adults = request.GET.get("num_adults")

        search = HotelSpecificSearch(
            hotel_id=hotel_code, checkin_date=checkin, checkout_date=checkout, occupancy=RoomOccupancy(num_adults, 0)
        )
        response = self.hotel_service.search_by_id(search)

        return Response(HotelSearchResponse.Schema().dump(response))

    @action(detail=False, methods=["POST"], name="Hotel Booking")
    def booking(self, request):
        booking_request = HotelBookingRequest.Schema().load(request.data)
        booking_response = self.hotel_service.booking(booking_request)

        return _response(booking_response, HotelBookingResponse)


class LocationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Geoname.objects.all()
    serializer_class = LocationsSerializer
    permission_classes = (HasOrganizationAPIKey,)
    throttle_classes = (OrganizationApiThrottle,)

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


class AuthenticationView(viewsets.ViewSet):
    @action(detail=False, methods=["POST"], name="Create Anonymous API Key")
    def create_api_key(self, request):
        request = ApiAccessRequest.Schema().load(request.data)
        if not request:
            return Response(status=400)

        response = api_access.create_anonymous_api_user(request)
        return _response(response, ApiAccessResponse)


def _response(obj, cls):
    return Response(cls.Schema().dump(obj))
