from rest_framework import routers

from apps.user import v1_views


router = routers.DefaultRouter()
router.register(r'', v1_views.UserViewSet, basename='users')

urlpatterns = router.urls
