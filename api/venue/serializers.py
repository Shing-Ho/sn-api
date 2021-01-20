from rest_framework import serializers
from api.models.models import Venue, VenueMedia


# Venue Serializer
class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = (
            "venue_id", "name", "venue_from", "type", "language_code", "tags",
            "status", "created_at", "modified_at", "created_by", "modified_by"
        )

class VenueMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueMedia
        fields = "__all__"