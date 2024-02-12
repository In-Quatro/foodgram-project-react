from django.db import models
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField

from users.models import User
from foodgram.constants import (
    BASE_NAME_LENGTH,
    SLUG_LENGTH,
    TEXT_LENGTH,
    MEASUREMENT_UNIT_LENGTH
)


class Ingredient(models.Model):
    """Модель Ингредиентов."""
    name = models.CharField(
        max_length=BASE_NAME_LENGTH,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель Тегов."""
    name = models.CharField(
        max_length=BASE_NAME_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=SLUG_LENGTH,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=BASE_NAME_LENGTH,
        verbose_name='Название рецепта'
    )
    text = models.CharField(
        max_length=TEXT_LENGTH,
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Время приготовления должно быть не меньше 1 минуты'
            )
        ]
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        blank=True,
        verbose_name='Фото'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=(
            'recipe',
            'ingredient',
        ),
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи Recipe и Ingredient."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Количество ингредиентов должно быть не меньше 1'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"


class BaseFovoriteShoppingCart(models.Model):
    """Базовая абстрактная модель для Избранного и Корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class Favorite(BaseFovoriteShoppingCart):
    """Модель Избранного."""
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites_recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name}'


class ShoppingCart(BaseFovoriteShoppingCart):
    """Модель Корзины."""
    class Meta:
        verbose_name = 'Корзина для покупок'
        verbose_name_plural = 'Корзины для покупок'
        default_related_name = 'recipes_in_cart'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user_cart'
            )
        ]

    def __str__(self):
        return (f'Пользователь "{self.user.username}" '
                f'добавил {self.recipe} в Корзину')
