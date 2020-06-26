from datetime import date

from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.models.models import Geoname, GeonameAlternateName
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


def index(request):
    return HttpResponse(status=404)


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
            HotelLocationSearch(location, checkin, checkout, num_adults=num_adults)
        )
        serializer = serializers.HotelAdapterHotelSerializer(instance=hotels, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["GET"], name="Search Hotels")
    def search_by_id(self, request):
        hotel_code = request.GET.get("hotel_code")
        checkin = date.fromisoformat(request.GET.get("checkin"))
        checkout = date.fromisoformat(request.GET.get("checkout"))
        num_adults = request.GET.get("num_adults")

        search = HotelSpecificSearch(hotel_code, checkin, checkout, RoomOccupancy(num_adults, 0))
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
