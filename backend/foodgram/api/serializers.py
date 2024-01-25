from rest_framework import serializers

from users.models import User, Subscription
from recipes.models import RecipeIngredient, Recipe, Tag, Ingredient


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователей."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class UserReadSerializer(BaseUserSerializer):
    """Сериализатор для получения информации о пользователях."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = BaseUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class SetPasswordSerializator(serializers.Serializer):
    """Сериализатор для изменения пароля текущего пользователя."""
    new_password = serializers.CharField(
        required=True
    )
    current_password = serializers.CharField(
        required=True
    )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов."""
    class Meta:
        model = Tag
        fields = '__all__'



class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(read_only=True, many=True)
    # tags = TagSerializer(many=True)
    author = UserReadSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'