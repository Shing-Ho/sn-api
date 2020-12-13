from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request

from api.auth.authentication import HasOrganizationAPIKey, OrganizationApiDailyThrottle, OrganizationApiBurstThrottle
from api.common.common_models import from_json
from api.search import search
from api.search.search_models import SearchRequest
from api.view.default_view import _response


class AllProductsViewSet(viewsets.ViewSet):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (HasOrganizationAPIKey,)
    throttle_classes = (OrganizationApiDailyThrottle, OrganizationApiBurstThrottle)

    @action(detail=False, url_path="search", methods=["POST"], name="Search All Products")
    def search(self, request: Request):
        request = from_json(request.data, SearchRequest)
        results = search.search_request(request)

        return _response(results)
