from django.contrib import admin
from django.urls import path, include
from rest_framework_extensions.routers import ExtendedSimpleRouter

import api.view.hotels_view
import api.view.search_views
import api.view.locations
import api.view.default_view
import api.view.charging_view
import api.view.carey_view
import api.accounts.views
import api.view.admin_view
from api.view import venue_view
from api.utils.documentations import prepare_schema

router = ExtendedSimpleRouter()
(
    router.register(r'', venue_view.VenueViewSet)
          .register(r'media',
                    venue_view.VenueMediaViewSet,
                    'venue_id',
                    parents_query_lookups=['venue_id'])
)
(
    router.register(r'', venue_view.VenueViewSet)
          .register(r'contact',
                    venue_view.VenueContactViewSet,
                    'venue_id',
                    parents_query_lookups=['venue_id'])
)
(
    router.register(r'', venue_view.VenueViewSet)
          .register(r'details',
                    venue_view.VenueDetailViewSet,
                    'venue_id',
                    parents_query_lookups=['venue_id'])
)
urlpatterns = router.urls