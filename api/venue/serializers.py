from rest_framework import serializers
from api.accounts.serializers import UserSerializer
from api.models import models


# Venue Serializer


class VenueMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VenueMedia
        fields = "__all__"


class VenueContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VenueContact
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentMethod
        fields = "__all__"


class VenueDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VenueDetail
        fields = "__all__"


class ProductGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductGroup
        fields = "__all__"


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductMedia
        fields = "__all__"


class ProductsNightLifeSerializer(serializers.ModelSerializer):
    media = ProductMediaSerializer(many=True, read_only=True)
    group = serializers.SerializerMethodField(source="get_group")

    class Meta:
        model = models.ProductsNightLife
        fields = "__all__"

    def get_group(self, obj):
        return obj.name


class VenueSerializer(serializers.ModelSerializer):
    media = VenueMediaSerializer(many=True, read_only=True)
    details = VenueDetailSerializer(many=True, read_only=True)
    contacts = VenueContactSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    products = ProductsNightLifeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Venue
        fields = "__all__"
