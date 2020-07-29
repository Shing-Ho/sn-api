from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.auth.models import HasOrganizationAPIKey, OrganizationApiThrottle
from api.booking import booking_service
from api.booking.booking_model import HotelBookingRequest
from api.common.models import RoomOccupancy
from api.hotel.adapters import hotel_service, translate
from api.hotel.adapters.translate.google.models import GoogleHotelSearchRequest
from api.hotel.hotel_model import HotelLocationSearch, HotelSpecificSearch, Hotel
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
        google_search_request: GoogleHotelSearchRequest = GoogleHotelSearchRequest.Schema().load(request.data)
        request = HotelSpecificSearch(
            hotel_id=google_search_request.hotel_id,
            start_date=google_search_request.start_date,
            end_date=google_search_request.end_date,
            occupancy=RoomOccupancy(
                adults=google_search_request.party.adults, children=len(google_search_request.party.children)
            ),
            daily_rates=False,
        )

        response = hotel_service.search_by_id(request)
        google_response = translate.google.translate.translate_hotel_response(google_search_request, response)

        return _response(google_response)

    @action(detail=False, url_path="booking", methods=["POST"], name="Hotel Booking")
    def booking(self, request):
        booking_request = HotelBookingRequest.Schema().load(request.data)
        booking_response = booking_service.book(booking_request)

        return _response(booking_response)
