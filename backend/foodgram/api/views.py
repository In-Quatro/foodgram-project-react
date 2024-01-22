from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from api.serializers import (
    UserSerializer,
    RecipeIngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
)

from users.models import User, Subscription
from recipes.models import (
    RecipeIngredient,
    Recipe,
    Tag,
    Ingredient,

)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# class RecipeIngredientViewSet(viewsets.ModelViewSet):
#     queryset = RecipeIngredient.objects.all()
#     serializer_class = RecipeIngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer