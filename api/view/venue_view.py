from api.models.models import (
    Venue,
    VenueMedia,
    VenueContact,
    PaymentMethod,
    VenueDetail,
    ProductGroup,
    ProductsNightLifeMedia,
    ProductsNightLife,
    ProductHotel,
    ProductHotelsMedia,
    ProductsHotelRoomDetails,
    ProductsHotelRoomPricing,
)
from api.venue import serializers
from rest_framework import viewsets
from api.auth.authentication import IsOwner
from api.utils.paginations import ObjectPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

# from django_filters.rest_framework import DjangoFilterBackend


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


class ProductNightLifeMediaViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductsNightLifeMedia.objects.filter()
    serializer_class = serializers.ProductNightLifeMediaSerializer
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


class ProductHotelMediaViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductHotelsMedia.objects.filter()
    serializer_class = serializers.ProductHotelsMediaSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class ProductHotelViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductHotel.objects.filter()
    serializer_class = serializers.ProductHotelSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]


class ProductsHotelRoomDetailsViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductsHotelRoomPricing.objects.filter()
    serializer_class = serializers.ProductsHotelRoomPricingSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['product_hotels']


class ProductsHotelRoomPricingDetailsViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = ProductsHotelRoomDetails.objects.filter()
    serializer_class = serializers.ProductsHotelRoomDetailsSerializer
    pagination_class = ObjectPagination
    http_method_names = ["get", "post", "put", "delete"]
