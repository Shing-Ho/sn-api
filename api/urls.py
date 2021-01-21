from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

import api.view.hotels_view
import api.view.search_views
import api.view.locations
import api.view.default_view
import api.view.charging_view
import api.view.carey_view
import api.accounts.views
import api.view.admin_view
import api.view.venue_view
from api.utils.documentations import prepare_schema

router = routers.SimpleRouter(trailing_slash=False)

schema_view = prepare_schema()

router.register(r"locations", api.view.locations.LocationsViewSet, basename="locations")
router.register(r"hotels", api.view.hotels_view.HotelViewSet, basename="hotels")
router.register(r"search", api.view.search_views.AllProductsViewSet, basename="search")
router.register(r"charging", api.view.charging_view.ChargingViewSet, basename="charging")
router.register(r"carey", api.view.carey_view.CareyViewSet, basename="carey")
router.register(r"authentication", api.view.default_view.AuthenticationView, basename="authentication")
router.register(r"users", api.view.admin_view.UserViewSet, basename="user-list")
router.register(r"venues", api.view.venue_view.VenueViewSet, basename="venue-list")
router.register(r"venue-media", api.view.venue_view.VenueMediaViewSet, basename="venue-media-list")

router.urls.append(path("accounts/", include("api.accounts.urls")))

urlpatterns = [
    path("", api.view.default_view.index),
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
