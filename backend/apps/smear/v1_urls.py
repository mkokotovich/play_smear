from rest_framework import routers

from apps.smear import v1_views

router = routers.DefaultRouter()
router.register(r'games', v1_views.GameViewSet, basename='games')
router.register(r'games/(?P<game_id>[0-9-]+)/teams', v1_views.TeamViewSet, basename='teams')
router.register(r'games/(?P<game_id>[0-9-]+)/hands/(?P<hand_id>[0-9-]+)/bids', v1_views.BidViewSet, basename='bids')
router.register(r'games/(?P<game_id>[0-9-]+)/hands/(?P<hand_id>[0-9-]+)/tricks/(?P<trick_id>[0-9-]+)/plays', v1_views.PlayViewSet, basename='plays')

urlpatterns = router.urls
