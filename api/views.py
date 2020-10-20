from typing import List, Union

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import api_access
from .api_access import ApiAccessRequest
from .common.models import SimplenightModel, to_json


def index(request):
    return HttpResponse(status=404)


class AuthenticationView(viewsets.ViewSet):
    @action(detail=False, methods=["POST"], name="Create Anonymous API Key")
    def create_api_key(self, request):
        request = ApiAccessRequest.parse_raw(request.data)
        if not request:
            return Response(status=400)

        response = api_access.create_anonymous_api_user(request)
        return _response(response)


def _response(obj: Union[SimplenightModel, List[SimplenightModel]]):
    many = isinstance(obj, list)
    return HttpResponse(to_json(obj, many=many), content_type="application/json")
