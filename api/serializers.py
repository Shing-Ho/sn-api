from rest_framework import serializers

from .hotel.hotel_model import HotelAdapterHotel, Address, HotelRate
from .models.models import Geoname, supplier_hotels, pmt_transaction


class payments_serializer(serializers.ModelSerializer):
    charge = serializers.CharField(max_length=900)

    class Meta:
        model = pmt_transaction

        fields = "__all__"


class mappingcodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = supplier_hotels
        fields = "__all__"


class LocationAlternateNameSerializer(serializers.StringRelatedField):
    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        return {"language_code": value.iso_language_code, "name": value.name}


class LocationsSerializer(serializers.ModelSerializer):
    primary_name = serializers.CharField(source="location_name")
    localization = LocationAlternateNameSerializer(many=True, read_only=True, source="lang")

    class Meta:
        model = Geoname
        fields = ("id", "iso_country_code", "primary_name", "localization", "latitude", "longitude")


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
