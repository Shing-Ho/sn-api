from rest_framework import serializers

from .common.models import Address, HotelRate
from .hotel.hotel_model import HotelAdapterHotel
from .models.models import Geoname, supplier_hotels


class mappingcodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = supplier_hotels
        fields = "__all__"


class StringListField(serializers.ListField):
    child = serializers.CharField()


class HotelAdapterHotelAddressSerializer(serializers.Serializer):
    city = serializers.CharField()
    province = serializers.CharField()
    postal_code = serializers.CharField()
    country = serializers.CharField()
    address1 = serializers.CharField()
    address2 = serializers.CharField()
    address3 = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return Address(**validated_data)


class HotelAdapterHotelRateSerializer(serializers.Serializer):
    total_price = serializers.FloatField()
    taxes = serializers.FloatField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return HotelRate(**validated_data)


class HotelAdapterHotelSerializer(serializers.Serializer):
    name = serializers.CharField()
    chain_code = serializers.CharField(max_length=2)
    address = HotelAdapterHotelAddressSerializer()
    rate = HotelAdapterHotelRateSerializer()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return HotelAdapterHotel(**validated_data)
