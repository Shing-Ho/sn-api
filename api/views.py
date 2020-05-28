from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from api.models.models import Hotels
from .serializers import (HotelsSerializer,)
def index(request):
    return HttpResponse("Hello, World!  This is the index page")


def detail(request):

    return HttpResponse("there are currently {} Hotelss in the Hotels model".format(Hotels.objects.all().count()))


class HotelsViewset(viewsets.ModelViewSet):
    queryset = Hotels.objects.all()
    serializer_class = HotelsSerializer

    def get_queryset(self):
        queryset = self.queryset
        locations = self.request.GET.get('locations')
        minstars = self.request.GET.get("minstars")
        if locations:
            queryset = queryset.filter(city=locations)
        if minstars:
            queryset = queryset.filter(stars__gt=minstars)
        return queryset
