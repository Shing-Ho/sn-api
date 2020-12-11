from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request

from api.activities import activity_search
from api.auth.authentication import HasOrganizationAPIKey, OrganizationApiDailyThrottle, OrganizationApiBurstThrottle
from api.common.common_models import from_json
from api.search.search_models import ActivityLocationSearch
from api.view.default_view import _response


class AllProductsViewSet(viewsets.ViewSet):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (HasOrganizationAPIKey,)
    throttle_classes = (OrganizationApiDailyThrottle, OrganizationApiBurstThrottle)

    @action(detail=False, url_path="search", methods=["POST"], name="Search Activities")
    def search(self, request: Request):
        request = from_json(request.data, ActivityLocationSearch)
        activities = activity_search.search_by_location(request)

        return _response(activities)
