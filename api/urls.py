from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

import api.view.hotels_view
import api.view.search_views
import api.view.locations
import api.view.default_view
import api.view.charging_view
import api.view.carey_view

router = routers.SimpleRouter(trailing_slash=False)


router.register(r"locations", api.view.locations.LocationsViewSet, basename="locations")
router.register(r"hotels", api.view.hotels_view.HotelViewSet, basename="hotels")
router.register(r"search", api.view.search_views.AllProductsViewSet, basename="search")
router.register(r"charging", api.view.charging_view.ChargingViewSet, basename="charging")
router.register(r"carey", api.view.carey_view.CareyViewSet, basename="carey")
router.register(r"authentication", api.view.default_view.AuthenticationView, basename="authentication")

urlpatterns = [
    path("", api.view.default_view.index),
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
]
