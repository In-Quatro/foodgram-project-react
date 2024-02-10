from django_filters.rest_framework import filters, FilterSet
from rest_framework.filters import SearchFilter
from recipes.models import Recipe, Tag


class IngredientFilter(SearchFilter):
    """Поиск по названию Ингредиента."""
    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтр по полю is_favorited и is_in_shopping_cart."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
        )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites_recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipes_in_cart__user=user)
        return queryset
