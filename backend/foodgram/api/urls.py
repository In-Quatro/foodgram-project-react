from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter
from .views import (
    UsersViewSet,
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
    SubscriptionViewSet
)

v1_router = DefaultRouter()

v1_router.register('users/subscriptions', SubscriptionViewSet)
# http://localhost:63342/api/users/{id}/subscribe/
v1_router.register('users', UsersViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(v1_router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]