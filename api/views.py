import json
from datetime import date
import stripe
from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from uszipcode import SearchEngine

from api.hotel.adapters.travelport.travelport import TravelportHotelAdapter
from api.models.models import Geoname, GeonameAlternateName
from api.models.models import supplier_hotels, pmt_transaction
from . import api_access
from .api_access import ApiAccessRequest, ApiAccessResponse
from .auth.models import HasOrganizationAPIKey, OrganizationApiThrottle
from .hotel.adapters.hotel_service import HotelService
from .hotel.hotels import (
    HotelLocationSearch,
    HotelSpecificSearch,
    RoomOccupancy,
    HotelSearchResponseHotel,
    HotelBookingRequest,
    HotelBookingResponse,
)
from .serializers import (
    LocationsSerializer,
)
from .serializers import mappingcodesSerializer, paymentsSerializer

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


class paymentsViewSet(viewsets.ModelViewSet):

    queryset = pmt_transaction.objects.all()
    serializer_class = paymentsSerializer

    @action(detail=True, methods=['post'])
    def create_charge(self, request):
        amt = self.request.GET.get("amount")
        currency = self.request.GET.get("currency")
        pmt_source_token = self.request.GET.get("pmt_source_token")
        if amt and if current and if pmt_source_token:
            return stripe.Charge.create(amount=amt, currency="USD", source=pmt_source_token, description=booking_id)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


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
    hotel_adapter = TravelportHotelAdapter()
    hotel_service = HotelService("stub")

    @action(detail=False, url_path="search-by-location", methods=["GET", "POST"], name="Search Hotels")
    def search_by_location(self, request: Request):
        if request.data:
            request = HotelLocationSearch.Schema().load(request.data)
        else:
            location = request.GET.get("location")
            checkin = request.GET.get("checkin")
            checkout = request.GET.get("checkout")
            num_adults = request.GET.get("num_adults")
            num_children = request.GET.get("num_adults")
            crs = request.GET.get("crs")

            request = HotelLocationSearch(
                location_name=location,
                start_date=date.fromisoformat(checkin),
                end_date=date.fromisoformat(checkout),
                occupancy=RoomOccupancy(adults=num_adults, children=num_children),
                daily_rates=False,
                crs=crs
            )

        hotels = self.hotel_service.search_by_location(request)

        return Response(HotelSearchResponseHotel.Schema(many=True).dump(hotels))

    @action(detail=False, url_path="search-by-id", methods=["GET", "POST"], name="Search Hotels")
    def search_by_id(self, request):
        if request.data:
            request = HotelSpecificSearch.Schema().load(request.data)
        else:
            hotel_code = request.GET.get("location")
            checkin = request.GET.get("checkin")
            checkout = request.GET.get("checkout")
            num_adults = request.GET.get("num_adults")
            num_children = request.GET.get("num_adults")
            crs = request.GET.get("crs")

            request = HotelSpecificSearch(
                hotel_id=hotel_code,
                start_date=date.fromisoformat(checkin),
                end_date=date.fromisoformat(checkout),
                occupancy=RoomOccupancy(adults=num_adults, children=num_children),
                daily_rates=False,
                crs=crs
            )

        response = self.hotel_service.search_by_id(request)

        return Response(HotelSearchResponseHotel.Schema().dump(response))

    @action(detail=False, url_path="booking", methods=["POST"], name="Hotel Booking")
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
