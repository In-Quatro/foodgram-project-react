from rest_framework.views import APIView
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from api.serializers import (
    UserReadSerializer,
    BaseUserSerializer,
    RecipeIngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
)
from rest_framework.response import Response
from users.models import User, Subscription
from recipes.models import (
    RecipeIngredient,
    Recipe,
    Tag,
    Ingredient,
)


class ReadOnlyMixins(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,   # убрать поле после проверки
                 viewsets.GenericViewSet):
    """Миксин для [GET] метода."""
    pass


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для Пользователя."""
    queryset = User.objects.all()
    # serializer_class = UserReadSerializer

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return UserReadSerializer
        return BaseUserSerializer

    @action(methods=['get'], detail=False)
    def me(self, request, pk=2):
        user = User.objects.get(pk=pk)
        serializator = BaseUserSerializer(user)
        return Response(serializator.data)


# class RecipeIngredientViewSet(viewsets.ModelViewSet):
#     queryset = RecipeIngredient.objects.all()
#     serializer_class = RecipeIngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для Тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get', 'post']


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для Ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get', 'post']


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer