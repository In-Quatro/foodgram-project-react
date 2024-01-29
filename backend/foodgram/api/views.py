from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from api.serializers import (
    UserReadSerializer,
    UserSerializer,
    RecipeCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    SetPasswordSerializer,
    RecipeShopingFavoriteSerializer,
    RecipeReadSerializer,
)
from rest_framework.response import Response
from users.models import User, Subscription
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
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

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserReadSerializer
        return UserSerializer

    @action(methods=['get'],
            detail=False)
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=False,)
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для Рецептов."""
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(
            recipe=recipe,
            user=request.user).exists()
        if request.method == 'POST':
            if favorite:
                return Response(
                    {'errors': 'Данный рецепт уже в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeShopingFavoriteSerializer(
                recipe,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            delete_recipe = get_object_or_404(
                Favorite,
                user=request.user,
                recipe=recipe
            )
            delete_recipe.delete()
            return Response(
                {'detail': 'Рецепт удален из избранного.'},
                status=status.HTTP_204_NO_CONTENT)


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
    """ViewSet для Подписки."""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
