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
    def interaction_recipe(request, pk, model):
        """Вспомогательный метод
        для добавления Рецепта в Избранное и Корзину."""
        title_1, title_2 = '', ''
        if model.__name__ == 'Favorite':
            title_1, title_2 = 'Избранном', 'Избранного'
        elif model.__name__ == 'ShoppingCart':
            title_1, title_2 = 'Корзине', 'Корзины'
        try:
            recipe = Recipe.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'recipe': f'Недопустимый первичный ключ "{pk}" '
                          f'- объект не существует.'})
        presence_object = model.objects.filter(
            recipe=recipe,
            user=request.user).exists()
        if request.method == 'POST':
            if presence_object:
                return Response(
                    {'errors': f'Данный рецепт уже в {title_1}!'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            model.objects.create(user=request.user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not presence_object:
                return Response(
                    {'errors': f'Рецепт нельзя удалить из {title_2}, '
                               f'поскольку его нет в {title_1}.'},
                    status=status.HTTP_400_BAD_REQUEST)
            delete_recipe = get_object_or_404(
                model,
                user=request.user,
                recipe=recipe
            )
            delete_recipe.delete()
            return Response(
                {'detail': f'Рецепт удален из {title_2}.'},
                status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        return self.interaction_recipe(request, pk, Favorite)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        return self.interaction_recipe(request, pk, ShoppingCart)

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
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet для Ингредиента."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    http_method_names = ('get', )
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None
