from django.contrib import admin

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    Favorite
)

from users.models import User, Subscription

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(Favorite)