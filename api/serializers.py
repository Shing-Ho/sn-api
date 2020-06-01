from rest_framework import serializers
from .models.models import Hotels, Geoname, GeonameAlternateName


class HotelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotels
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

