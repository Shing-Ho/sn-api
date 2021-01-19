from rest_framework import serializers
from api.models.models import Venue, VenueImage


# Venue Serializer
class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = (
            "venue_id", "name", "venue_from", "venue_type", "language_code", "tags",
            "status", "created_at", "modified_at", "created_by", "modified_by"
        )

class VenueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImage
        fields = "__all__"