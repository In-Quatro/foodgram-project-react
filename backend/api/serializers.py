from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription, User


class AbstractModelSerializer(serializers.ModelSerializer):
    """Абстрактный Serializer для моделей
    Subscription, ShoppingCart, Favorite."""
    def get_field(self, obj, model):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            if model.__name__ == 'Subscription':
                return model.objects.filter(
                    user=request.user,
                    author=obj).exists()
            elif model.__name__ in ('ShoppingCart', 'Favorite'):
                return model.objects.filter(
                    user=request.user,
                    recipe=obj).exists()
        return False

    class Meta:
        abstract = True


class CustomUserReadSerializer(UserSerializer, AbstractModelSerializer):
    """Serializer для получения информации о Пользователях."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return self.get_field(obj, Subscription)


class CustomUserSerializer(UserCreateSerializer):
    """Serializer для создания Пользователя."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class SetPasswordSerializer(serializers.Serializer):
    """Serializer для изменения пароля текущего пользователя."""
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        """Изменение пароля."""
        current_password = validated_data['current_password']
        new_password = validated_data['new_password']

        instance.password = validated_data.get('password', instance.password)
        if not instance.check_password(current_password):
            raise serializers.ValidationError(
                {'current_password': 'Текущий пароль введен не верно!'})
        if current_password == new_password:
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль совпадает с текущим! '
                                 'Введите другой пароль.'})
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class TagSerializer(serializers.ModelSerializer):
    """Serializer для просмотра Тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer для связанных моделей Recipe и Ingredient."""
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer для получения Ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Serializer для получения Ингредиентов с количеством."""
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeReadSerializer(AbstractModelSerializer):
    """Serializer для получения списка рецептов."""
    tags = TagSerializer(
        many=True,
        read_only=True,)
    author = CustomUserReadSerializer(
        read_only=True,)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='recipes')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

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

    def get_is_favorited(self, obj):
        return self.get_field(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_field(obj, ShoppingCart)


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания Ингредиентов с их количеством."""
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания, изменения и удаления Рецептов."""
    id = serializers.ReadOnlyField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = CustomUserReadSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True,)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, obj):
        tags = obj.get('tags', [])
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Теги не должны '
                        'повторяться в рецепте.'})
        ingredients = obj.get('ingredients', [])
        unique_ingredient = set()
        for ingredient in ingredients:
            id = ingredient.get('id')
            if id in unique_ingredient:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не должны '
                                   'повторяться в рецепте.'})
            unique_ingredient.add(id)
            try:
                Ingredient.objects.get(pk=id)
            except ObjectDoesNotExist:
                raise serializers.ValidationError({
                    'ingredients': f'Недопустимый первичный ключ "{id}"'
                                   f' - объект не существует.'})
        fields = [
            'ingredients',
            'tags',
        ]
        for field in fields:
            if not obj.get(field):
                raise serializers.ValidationError({
                    f'{field}': 'Поле обязательное и не может быть пустым!'})
        return obj

    @staticmethod
    def create_objects(recipe, tags, ingredients):
        """Вспомогательный метод для создания записей в БД."""
        recipe.tags.clear()
        for tag in tags:
            recipe.tags.add(tag)

        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            )
            recipe_ingredients.append(recipe_ingredient)

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Создание Рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_objects(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Изменение Рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        self.create_objects(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer для краткого отображения Рецепта."""
    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(AbstractModelSerializer):
    """Serializer для Подписок."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return self.get_field(obj, Subscription)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
