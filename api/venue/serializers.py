from rest_framework import serializers
from api.models import models


# Venue Serializer
class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Venue
        fields = (
            "venue_id", "name", "venue_from", "type", "language_code", "tags",
            "status", "created_at", "modified_at", "created_by", "modified_by"
        )

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
