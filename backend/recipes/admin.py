from django.contrib import admin

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона Ингредиентов."""
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-зона Тегов."""
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'name',
        'slug',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона Рецептов."""
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
        'pub_date',
        'is_favorites',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )

    @admin.display(description='Число добавлений в избранное')
    def is_favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админ-зона Ингредиентов в Рецепте."""
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'ingredient',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона Избранного."""
    list_display = (
        'id',
        'recipe',
        'user',
    )
    search_fields = (
        'recipe',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-зона Корзины."""
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = (
        'recipe',
    )
