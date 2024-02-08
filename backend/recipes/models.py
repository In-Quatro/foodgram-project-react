from django.db import models
from django.core.validators import MinValueValidator
from users.models import User

from .constants import (
    BASE_NAME_LENGTH,
    SLUG_LENGTH,
    TEXT_LENGTH,
    COLOR_LENGTH,
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
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель Тегов."""
    name = models.CharField(
        max_length=BASE_NAME_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=COLOR_LENGTH,
        verbose_name='Цвет тега',
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
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1)]
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

    is_favorited = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='В избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='В корзине'
    )

    class Meta:
        ordering = ['-pub_date']
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
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'


class Favorite(models.Model):
    """Модель Избранного."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранное'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь избранного'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe.name}'


class ShoppingCart(models.Model):
    """Модель Корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Корзина для покупок'
        verbose_name_plural = 'Корзины для покупок'

    def __str__(self):
        return (f'Пользователь "{self.user.username}" '
                f'добавил {self.recipe} в Корзину')
