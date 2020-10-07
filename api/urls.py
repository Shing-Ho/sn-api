from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from api.view.hotels import HotelViewSet
from api.view.locations import LocationsViewSet
from api.views import AuthenticationView

router = routers.SimpleRouter(trailing_slash=False)


router.register(r"locations", LocationsViewSet, basename="locations")
router.register(r"hotels", HotelViewSet, basename="hotels")
router.register(r"authentication", AuthenticationView, basename="authentication")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
]
