from rest_framework import routers

from apps.smear import v1_views


router = routers.DefaultRouter()
router.register(r'games', v1_views.GameViewSet, base_name='games')

urlpatterns = router.urls
