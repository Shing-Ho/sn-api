from django.contrib import admin
from api.view import venue_view
from django.urls import path, include

from rest_framework_extensions.routers import ExtendedSimpleRouter

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
(
    router.register(r'', venue_view.VenueViewSet)
        .register(r'product_group',
                venue_view.ProductGroupViewSet,
                'venue_id',
                parents_query_lookups=['venue_id'])
)
(
    router.register(r'', venue_view.VenueViewSet)
        .register(r'product_media',
                venue_view.ProductMediaViewSet,
                'venue_id',
                parents_query_lookups=['venue_id'])
)
(
    router.register(r'', venue_view.VenueViewSet)
        .register(r'product',
                venue_view.ProductNightLifeViewSet,
                'venue_id',
                parents_query_lookups=['venue_id'])
)
urlpatterns = router.urls