import csv

import os
from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Command for importing data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path', type=str, nargs='?', default='data/ingredients.csv'
        )

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, options['csv_path'])
        with open(csv_path, encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            new_objects = []
            existing_count = 0
            for name, measurement_unit in reader:
                if not Ingredient.objects.filter(
                        name=name,
                        measurement_unit=measurement_unit).exists():
                    new_objects.append(Ingredient(
                        name=name,
                        measurement_unit=measurement_unit))
                else:
                    existing_count += 1
            if new_objects:
                Ingredient.objects.bulk_create(new_objects)
                self.stdout.write(self.style.SUCCESS(
                    f'Добавление данных завершено. '
                    f'Добавлено {len(new_objects)} записей. '
                    f'{existing_count} записей уже существовало.'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    'Новых данных не было добавлено. '
                    'Все данные уже существуют в базе.'
                ))
