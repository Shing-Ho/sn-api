from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

import api.view.admin_view
import api.view.carey_view
import api.view.charging_view
import api.view.default_view
import api.view.hotels_view
import api.view.locations
import api.view.default_view
import api.view.charging_view
import api.view.carey_view
import api.accounts.views
from api.view import venue_view
from rest_framework.schemas import get_schema_view

router = routers.SimpleRouter(trailing_slash=False)


router.register(r"locations", api.view.locations.LocationsViewSet, basename="locations")
router.register(r"hotels", api.view.hotels_view.HotelViewSet, basename="hotels")
router.register(r"multi", api.view.multi_product_views.AllProductsViewSet, basename="multi")
router.register(r"charging", api.view.charging_view.ChargingViewSet, basename="charging")
router.register(r"carey", api.view.carey_view.CareyViewSet, basename="carey")
router.register(r"authentication", api.view.default_view.AuthenticationView, basename="authentication")
router.register(r"users", api.view.admin_view.UserViewSet, basename="user-list")
router.register(r"payment-methods", venue_view.PaymentMethodViewSet, basename="payment-methods-list")

router.urls.append(path("accounts/", include("api.accounts.urls")))
router.urls.append(path("venues/", include("api.venue.urls")))
urlpatterns = [
    path("", api.view.default_view.index),
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path('openapi', get_schema_view(
        title="Simplenight Hotel API",
        description="Test data",
        version="1.0.0"
    ), name='openapi-schema'),
]
