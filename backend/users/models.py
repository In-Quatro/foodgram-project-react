from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


from foodgram.constants import (
    USERNAME_LENGTH,
    EMAIL_LENGTH,
    FIRST_NAME_LENGTH,
    LAST_NAME_LENGTH
)

username_validator = UnicodeUsernameValidator()


class User(AbstractUser):
    """Модель Пользователя."""
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=[username_validator],
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=LAST_NAME_LENGTH,
        verbose_name='Фамилия'
    )
    is_subscribed = models.BooleanField(
        blank=True,
        default=False,
        verbose_name='Подписан'
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель Подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_by',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Запрещено подписываться на самого себя!')

        if Subscription.objects.filter(user=self.user,
                                       author=self.author).exists():
            raise ValidationError(f'Вы уже подписаны на "{self.author}"!')
