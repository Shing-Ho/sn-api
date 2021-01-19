from api import logger
from rest_framework import viewsets
from api.models.models import Venue
from api.venue.serializers import VenueSerializer
from api.utils.paginations import ObjectPagination  
from rest_framework.permissions import IsAuthenticated
from api.auth.authentication import IsOwner, IsSuperUser   

class VenueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,]
    queryset = Venue.objects.filter()
    serializer_class = VenueSerializer
    pagination_class = ObjectPagination
    http_method_names = ['get', 'post', 'put','delete']

    def perform_create(self, serializer):
        """Sets the user profile to the logged in User."""
        serializer.save(created_by=self.request.user)

    # def get_queryset(self):
    #     return self.queryset.filter(created_by=self.request.user)

    def get_permissions(self):
        # print(self.action)
        if self.action == 'delete':
            self.permission_classes = [IsOwner,]
        elif self.action == 'retrieve':
            self.permission_classes = [IsOwner]
        elif self.action =="destroy":
            self.permission_classes = [IsOwner]
        elif self.action =="create":
            self.permission_classes = [IsOwner]


        return super(self.__class__, self).get_permissions()