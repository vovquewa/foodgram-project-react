"""
Модуль для импорта ингредиентов из csv файла

Формат csv файла:
    Название ингредиента, единица измерения

Разделитель полей: запятая

Пример:
    Мука, кг
    Сахар, кг
    Соль, г

Расположение csv файла: backend/data/ingredients.csv

Использование:
    python manage.py import_from_csv_ingredients

"""

from django.core.management.base import BaseCommand
from recipes.models import Ingredient
import csv

FILE_PATH = 'data/ingredients.csv'
FILE_NAME = 'ingredients.csv'


class Command(BaseCommand):
    help = 'Import ingredients from csv file'

    def handle(self, *args, **options):
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                ingredient = Ingredient(name=row[0], measurement_unit=row[1])
                ingredient.save()
        self.stdout.write(self.style.SUCCESS(f'Imported {FILE_NAME}'))
