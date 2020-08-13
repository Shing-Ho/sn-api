from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request

from api.auth.models import OrganizationApiThrottle, HasOrganizationAPIKey
from api.locations import location_service
from api.views import _response


class LocationsViewSet(viewsets.ViewSet):
    permission_classes = (HasOrganizationAPIKey,)
    throttle_classes = (OrganizationApiThrottle,)

    @action(detail=False, url_path="prefix", methods=["GET"], name="Search Locations by Prefix")
    def find_by_prefix(self, request: Request):
        lang_code = request.GET.get("lang_code", "en")
        prefix = request.GET.get("prefix")

        locations = location_service.find_by_prefix(prefix, lang_code)
        return _response(locations)

    @action(detail=False, url_path="id", methods=["GET"], name="Search Locations by Prefix")
    def find_by_id(self, request: Request):
        lang_code = request.GET.get("lang_code", "en")
        geoname_id = request.GET.get("location_id")

        locations = location_service.find_by_id(geoname_id, lang_code)
        return _response(locations)
