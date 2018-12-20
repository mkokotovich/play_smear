from django.conf.urls import url, include


urlpatterns = [
    url(r'^v1/', include('apps.user.v1_urls')),
]
