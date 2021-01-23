from api.view import venue_view
from rest_framework_extensions.routers import ExtendedSimpleRouter

router = ExtendedSimpleRouter(trailing_slash=False)
(
    router.register(r"", venue_view.VenueViewSet).register(
        r"media", venue_view.VenueMediaViewSet, "venue_id", parents_query_lookups=["venue_id"]
    )
)
(
    router.register(r"", venue_view.VenueViewSet).register(
        r"contact", venue_view.VenueContactViewSet, "venue_id", parents_query_lookups=["venue_id"]
    )
)
(
    router.register(r"", venue_view.VenueViewSet).register(
        r"details", venue_view.VenueDetailViewSet, "venue_id", parents_query_lookups=["venue_id"]
    )
)
(
    router.register(r"", venue_view.VenueViewSet).register(
        r"product-group", venue_view.ProductGroupViewSet, "venue_id", parents_query_lookups=["venue_id"]
    )
)
(
    router.register(r"", venue_view.VenueViewSet).register(
        r"product", venue_view.ProductNightLifeViewSet, "venue_id", parents_query_lookups=["venue_id"]
    )
)
(
    router.register(r"", venue_view.VenueViewSet)
    .register(r"product", venue_view.ProductNightLifeViewSet, "venue_id", parents_query_lookups=["venue_id"])
    .register(r"media", venue_view.ProductMediaViewSet, "id", parents_query_lookups=["product_id", "id"])
)
urlpatterns = router.urls
