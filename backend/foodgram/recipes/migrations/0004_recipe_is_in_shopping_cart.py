# Generated by Django 3.2 on 2024-01-30 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipe_is_favorited'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.BooleanField(blank=True, default=False, verbose_name='В корзине'),
        ),
    ]
