from api import logger
from rest_framework import viewsets
from api.auth.authentication import APIAdminPermission
from api.accounts.serializers import UserSerializer
from django.contrib.auth.models import User
from api.utils.paginations import ObjectPagination       

class UserViewSet(viewsets.ModelViewSet):
    permission_classes =[APIAdminPermission]
    queryset = User.objects.filter()
    serializer_class = UserSerializer
    pagination_class = ObjectPagination
    http_method_names = ['get', 'post', 'put','delete']