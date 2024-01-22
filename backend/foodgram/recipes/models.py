from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
        blank=True,
        unique=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=200,
        blank=True,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        unique=True,
        verbose_name='Цвет тега',
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        unique=True,
        verbose_name='Слаг тэга'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Название рецепта'
    )
    text = models.CharField(
        max_length=254,         # не обязательное поле
        blank=True,
        verbose_name='Описание рецепта'
    )
    cooking_time = models.IntegerField(
        blank=True,
        verbose_name='Время приготовления (в минутах)'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=True,
        null=True,
        default=None,
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
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
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
        ordering = ['-pub_date',]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента."""
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"

    class Meta:
        # ordering = ['-pub_date',]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
#
# class RecipeTag(models.Model):
#     """Промежуточная модель для связи рецепта и тега."""
#     tag = models.ForeignKey(
#         Tag,
#         on_delete=models.CASCADE,
#         verbose_name='Тег'
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         verbose_name='Рецепт'
#     )


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранное'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь избранного'
    )

    class Meta:
        # ordering = ['-pub_date',]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f"{self.recipe.name}"
