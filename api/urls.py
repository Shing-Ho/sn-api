from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from api.view.hotels import HotelViewSet
from api.view.locations import LocationsViewSet
from api.views import HotelBedsMap, AuthenticationView, PaymentsViewSet

router = routers.SimpleRouter()
router.register(r"payment", PaymentsViewSet, basename="payments")
router.register(r"locations", LocationsViewSet)
router.register(r"hotels", HotelViewSet, basename="hotels")
router.register(r"authentication", AuthenticationView, basename="authentication")
router.register(r"hotelbeds", HotelBedsMap, basename="hotelbeds")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
]
