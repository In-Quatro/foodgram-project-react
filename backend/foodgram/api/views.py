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
    ShoppingCart,
    RecipeIngredient,
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

    def interaction_recipe(self, request, pk, model):
        if model.__name__ == 'Favorite':
            message_add, message_del = 'Избранном', 'Избранного'
        elif model.__name__ == 'ShoppingCart':
            message_add, message_del = 'Корзине', 'Корзины'
        recipe = get_object_or_404(Recipe, id=pk)
        presence_object = model.objects.filter(
            recipe=recipe,
            user=request.user).exists()
        if request.method == 'POST':
            if presence_object:
                return Response(
                    {'errors': f'Данный рецепт уже в {message_add}!'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeShopingFavoriteSerializer(
                recipe,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            model.objects.create(user=request.user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            delete_recipe = get_object_or_404(
                model,
                user=request.user,
                recipe=recipe
            )
            delete_recipe.delete()
            return Response(
                {'detail': f'Рецепт удален из {message_del}.'},
                status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self.interaction_recipe(request, pk, Favorite)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        return self.interaction_recipe(request, pk, ShoppingCart)

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        objs = ShoppingCart.objects.filter(user=request.user)
        ing = [obj.recipe_id for obj in objs]
        print(ing)
        ing_2 = []
        for i in ing:
            ing_2.append(RecipeIngredient.objects.filter(id=i).values())
        print(ing_2)
        ii = Ingredient.objects.filter(id=2).values('name')

        print(list(ii))
        # 'id': 1, 'recipe_id': 1, 'ingredient_id': 1, 'amount': 10

        return Response(
            {'detail': 111},
            status=status.HTTP_200_OK)


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
