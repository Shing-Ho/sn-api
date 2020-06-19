"""API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from api import views
from .views import LocationsViewSet, HotelSupplierViewset, location_formater, Hotelbedmap

router = routers.SimpleRouter()
router2 = routers.SimpleRouter()

router.register(r"Locations", LocationsViewSet)
router.register(r"Suppliers", HotelSupplierViewset, basename="suppliers")
router2.register(r"hotelbeds",Hotelbedmap,basename="hotelbeds")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("iata/", location_formater, name="location_formater"),
    path("v0/", include(router2.urls)),
    path("api/v1/", include(router.urls)),
]
