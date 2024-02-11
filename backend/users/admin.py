from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ-зона Пользователей."""
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'get_subscribe_count',
        'get_recipe_count'
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'email',
    )

    def get_subscribe_count(self, obj):
        return obj.subscribed_to.count()

    get_subscribe_count.short_description = 'Кол-во подписчиков'

    def get_recipe_count(self, obj):
        return obj.recipes.count()

    get_recipe_count.short_description = 'Кол-во рецептов'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-зона Подписок."""
    list_display = (
        'id',
        'user',
        'author',
    )
