from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet

router = DefaultRouter()

router.register('users', UsersViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
