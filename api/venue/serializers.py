from rest_framework import serializers
from api.models import models

from django.contrib.auth.models import User

# from django.core.files.uploadedfile import InMemoryUploadedFile

# Venue Serializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "username", "is_staff", "is_superuser", "is_active")


class VenueMediaSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     file_fields = kwargs.pop('file_fields', None)
    #     super().__init__(*args, **kwargs)
    #     if file_fields:
    #         field_update_dict = {field: serializers.FileField
    # (required=False, write_only=True) for field in file_fields}
    #         self.fields.update(**field_update_dict)

    # def create(self, validated_data):
    #     validated_data_copy = validated_data.copy()
    #     validated_files = []
    #     for key, value in validated_data_copy.items():
    #         if isinstance(value, InMemoryUploadedFile):
    #             validated_files.append(value)
    #             validated_data.pop(key)
    #     submission_instance = super().create(validated_data)
    #     for file in validated_files:
    #         models.VenueMedia.objects.create(submission=submission_instance, file=file)
    #     return submission_instance

    class Meta:
        model = models.VenueMedia
        fields = "__all__"

    def to_representation(self, instance):
        rep = super(VenueMediaSerializer, self).to_representation(instance)
        rep["venue_id"] = instance.venue.id
        del rep["venue"]
        return rep


class VenueCreateMediaSerializer(serializers.ModelSerializer):
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

    def to_representation(self, instance):
        rep = super(ProductGroupSerializer, self).to_representation(instance)
        rep["venue_id"] = instance.venue.id
        del rep["venue"]
        return rep


class ProductNightLifeMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductsNightLifeMedia
        fields = "__all__"

    def to_representation(self, instance):
        rep = super(ProductNightLifeMediaSerializer, self).to_representation(instance)
        rep["venue_id"] = instance.venue.id
        del rep["venue"]
        return rep


class ProductHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductHotel
        fields = "__all__"

    def to_representation(self, instance):
        rep = super(ProductHotelSerializer, self).to_representation(instance)
        rep["venue_id"] = instance.venue.id
        del rep["venue"]
        return rep


class ProductHotelsMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductHotelsMedia
        fields = "__all__"


class ProductsNightLifeSerializer(serializers.ModelSerializer):
    # media = ProductMediaSerializer(many=True, read_only=True)
    group = serializers.SerializerMethodField(source="get_group")

    class Meta:
        model = models.ProductsNightLife
        fields = "__all__"

    def get_group(self, obj):
        return obj.name

    def to_representation(self, instance):
        rep = super(ProductsNightLifeSerializer, self).to_representation(instance)
        rep["venue_id"] = instance.venue.id
        del rep["venue"]
        return rep


class VenueSerializer(serializers.ModelSerializer):
    media = VenueMediaSerializer(many=True, read_only=True)
    details = VenueDetailSerializer(many=True, read_only=True)
    contacts = VenueContactSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    products = ProductsNightLifeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Venue
        fields = "__all__"


class ProductsSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField(source="get_group")

    class Meta:
        model = models.ProductsNightLife
        fields = "__all__"

    def get_group(self, obj):
        return obj.name


class ProductsHotelRoomDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductsHotelRoomDetails
        fields = "__all__"


class ProductsHotelRoomPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductsHotelRoomPricing
        fields = "__all__"
