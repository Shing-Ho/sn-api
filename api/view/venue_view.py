from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from api.models.models import (
    Venue,
    VenueMedia,
    VenueContact,
    PaymentMethod,
    VenueDetail,
    ProductGroup,
    ProductMedia,
    ProductsNightLife,
)
from api.venue import serializers
from api.utils.paginations import ObjectPagination
from rest_framework.permissions import IsAuthenticated
from api.auth.authentication import IsOwner


class VenueViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Venue.objects.filter()
    serializer_class = serializers.VenueSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]

    def perform_create(self, serializer):
        """Sets the user profile to the logged in User."""
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        # print(self.action)
        if self.action == "delete":
            self.permission_classes = [
                IsOwner,
            ]
        elif self.action == "destroy":
            self.permission_classes = [IsOwner]
        elif self.action == "create":
            self.permission_classes = [IsOwner]

        return super(self.__class__, self).get_permissions()


class VenueMediaViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = VenueMedia.objects.filter()
    serializer_class = serializers.VenueMediaSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class VenueContactViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = VenueContact.objects.filter()
    serializer_class = serializers.VenueContactSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class VenueDetailViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = VenueDetail.objects.filter()
    serializer_class = serializers.VenueDetailSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class PaymentMethodViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = PaymentMethod.objects.filter()
    serializer_class = serializers.PaymentMethodSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class ProductGroupViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductGroup.objects.filter()
    serializer_class = serializers.ProductGroupSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class ProductMediaViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductMedia.objects.filter()
    serializer_class = serializers.ProductMediaSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class ProductNightLifeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductsNightLife.objects.filter()
    serializer_class = serializers.ProductsNightLifeSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]
