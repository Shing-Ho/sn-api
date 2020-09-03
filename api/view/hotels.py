from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.auth.models import HasOrganizationAPIKey, OrganizationApiThrottle
from api.booking import booking_service
from api.booking.booking_model import HotelBookingRequest
from api.common.request_cache import get_request_cache
from api.hotel import converter, hotel_service
from api.hotel.converter.google_models import GoogleHotelSearchRequest, GoogleBookingSubmitRequest
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch
from api.views import _response


class HotelViewSet(viewsets.ViewSet):
    permission_classes = (HasOrganizationAPIKey,)
    throttle_classes = (OrganizationApiThrottle,)

    @action(detail=False, url_path="search-by-location", methods=["GET", "POST"], name="Search Hotels")
    def search_by_location(self, request: Request):
        request = HotelLocationSearch.Schema().load(request.data)
        hotels = hotel_service.search_by_location_frontend(request)

        return _response(hotels)

    @action(detail=False, url_path="search-by-id", methods=["GET", "POST"], name="Search Hotels")
    def search_by_id(self, request):
        request = HotelSpecificSearch.Schema().load(request.data)
        hotels = hotel_service.search_by_id_frontend(request)

        return _response(hotels)

    @action(detail=False, url_path="google/search-by-id", methods=["GET", "POST"], name="Search Hotels Google API")
    def search_by_id_google(self, request):
        google_search_request = GoogleHotelSearchRequest.Schema().load(request.data)
        search_request = converter.google.convert_hotel_specific_search(google_search_request)

        response = hotel_service.search_by_id(search_request)
        google_response = converter.google.convert_hotel_response(google_search_request, response)

        return _response(google_response)

    @action(detail=False, url_path="booking", methods=["POST"], name="Hotel Booking")
    def booking(self, request):
        booking_request = HotelBookingRequest.Schema().load(request.data)
        booking_response = booking_service.book(booking_request)

        return _response(booking_response)

    @action(detail=False, url_path="google/booking", methods=["POST"], name="GoogleHotel Booking")
    def booking_google(self, request):
        google_booking_request = GoogleBookingSubmitRequest.Schema().load(request.data)
        booking_request = converter.google.convert_booking_request(google_booking_request)
        booking_response = booking_service.book(booking_request)

        return _response(converter.google.convert_booking_response(google_booking_request, booking_response))

    @action(detail=False, url_path="status", methods=["GET"], name="Health Check")
    def status(self, _):
        """Simply sets a variable in LocMem request cache, and retrieves it, to ensure things are working"""
        request_cache = get_request_cache()
        organization = request_cache.get("organization")
        organization_name = organization.name
        request_cache.set("__status", f"OK {organization_name}")

        return Response(data=request_cache.get("__status"))
