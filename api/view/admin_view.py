from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from api import logger
from api.view.default_view import _response
from api.auth.authentication import APIAdminPermission
from api.accounts.serializers import UserSerializer
from django.contrib.auth.models import User
from api.utils.paginations import ObjectPagination       



class UserViewSet(viewsets.ModelViewSet):
    permission_classes =[APIAdminPermission]
    queryset = User.objects.filter()
    serializer_class = UserSerializer
    pagination_class = ObjectPagination

