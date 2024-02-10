import csv
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    TagSerializer,
)
from .filter import RecipeFilter, IngredientFilter
from .paginations import CustomPagination
from .permissions import IsAuthorPermission
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для Рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def check_recipe(pk, request, model):
        """Вспомогательный метод проверки Рецепта в БД."""
        try:
            recipe = Recipe.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'recipe': f'Недопустимый первичный ключ "{pk}" '
                          f'- объект не существует.'})
        presence_recipe = model.objects.filter(
            recipe=recipe,
            user=request.user).exists()
        return recipe, presence_recipe

    @staticmethod
    def add_recipe(pk, request, model):
        """Вспомогательный метод добавления Рецепта в Избранное и Корзину."""
        recipe,  presence_recipe = RecipeViewSet.check_recipe(
            pk, request, model
        )
        serializer = RecipeSerializer(
            recipe,
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        if presence_recipe:
            return Response(
                {'errors': f'Данный рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=request.user, recipe=recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_recipe(pk, request, model):
        """Вспомогательный метод удаления Рецепта из Избранного и Корзины."""
        recipe, presence_recipe = RecipeViewSet.check_recipe(
            pk, request, model
        )
        if not presence_recipe:
            return Response(
                {'errors': 'Рецепт нельзя удалить, '
                           'поскольку его нет в списке!'},
                status=status.HTTP_400_BAD_REQUEST)
        delete_recipe = get_object_or_404(
            model,
            user=request.user,
            recipe=recipe
        )
        delete_recipe.delete()
        return Response(
            {'detail': f'Рецепт удален.'},
            status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Добавить рецепт в Избранное."""
        return self.add_recipe(pk, request, Favorite)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удалить рецепт из Избранного."""
        return self.delete_recipe(pk, request, Favorite)

    @action(methods=['post'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в Корзину."""
        return self.add_recipe(pk, request, ShoppingCart)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удалить рецепт из Корзины."""
        return self.delete_recipe(pk, request, ShoppingCart)

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        ingredients_obj = RecipeIngredient.objects.filter(
            recipe__recipes_in_cart__user=request.user
        ).values('ingredient'
                 ).annotate(total_amount=Sum('amount')
                            ).values_list('ingredient__name',
                                          'total_amount',
                                          'ingredient__measurement_unit')
        data = [ingredients for ingredients in ingredients_obj]

        filename = 'recipe.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
            writer.writerows(data)

        response = HttpResponse(open(filename, 'rb'), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response






class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для Тега."""
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    http_method_names = ('get',)


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для Ингредиента."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    http_method_names = ('get', )
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
