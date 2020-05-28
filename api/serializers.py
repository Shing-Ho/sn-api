from rest_framework import serializers
from .models.models import Hotels


class HotelsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotels
        fields = ('__all__')
