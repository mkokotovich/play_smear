from rest_framework import routers

from apps.smear import v1_views


router = routers.DefaultRouter()
router.register(r'games', v1_views.GameViewSet, base_name='games')
router.register(r'games/(?P<game_id>[0-9-]+)/teams', v1_views.TeamViewSet, base_name='teams')
router.register(r'games/(?P<game_id>[0-9-]+)/hands/(?P<hand_id>[0-9-]+)/bids', v1_views.BidViewSet, base_name='bids')

urlpatterns = router.urls
