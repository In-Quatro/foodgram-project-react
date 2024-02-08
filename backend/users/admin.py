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
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'email',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-зона Подписок."""
    list_display = (
        'id',
        'user',
        'author',
    )
