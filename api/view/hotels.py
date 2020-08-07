from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.auth.models import HasOrganizationAPIKey, OrganizationApiThrottle
from api.booking import booking_service
from api.booking.booking_model import HotelBookingRequest
from api.hotel import translate
from api.hotel.adapters import hotel_service
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch, Hotel
from api.hotel.translate.google_models import GoogleHotelSearchRequest, GoogleBookingSubmitRequest
from api.views import _response


class HotelViewSet(viewsets.ViewSet):
    permission_classes = (HasOrganizationAPIKey,)
    throttle_classes = (OrganizationApiThrottle,)

    @action(detail=False, url_path="search-by-location", methods=["GET", "POST"], name="Search Hotels")
    def search_by_location(self, request: Request):
        request = HotelLocationSearch.Schema().load(request.data)
        hotels = hotel_service.search_by_location(request)

        return Response(Hotel.Schema(many=True).dump(hotels))

    @action(detail=False, url_path="search-by-id", methods=["GET", "POST"], name="Search Hotels")
    def search_by_id(self, request):
        request = HotelSpecificSearch.Schema().load(request.data)
        hotels = hotel_service.search_by_id(request)

        return _response(hotels)

    @action(detail=False, url_path="google/search-by-id", methods=["GET", "POST"], name="Search Hotels Google API")
    def search_by_id_google(self, request):
        google_search_request = GoogleHotelSearchRequest.Schema().load(request.data)
        search_request = translate.google.translate_hotel_specific_search(google_search_request)

        response = hotel_service.search_by_id(search_request)
        google_response = translate.google.translate_hotel_response(google_search_request, response)

        return _response(google_response)

    @action(detail=False, url_path="booking", methods=["POST"], name="Hotel Booking")
    def booking(self, request):
        booking_request = HotelBookingRequest.Schema().load(request.data)
        booking_response = booking_service.book(booking_request)

        return _response(booking_response)

    @action(detail=False, url_path="google/booking", methods=["POST"], name="GoogleHotel Booking")
    def booking_google(self, request):
        google_booking_request = GoogleBookingSubmitRequest.Schema().load(request.data)
        booking_request = translate.google.translate_booking_request(google_booking_request)
        booking_response = booking_service.book(booking_request)

        return _response(translate.google.translate_booking_response(google_booking_request, booking_response))