"""
Модуль очистки модели Ingredient
"""

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Clear ingredients'

    def handle(self, *args, **options):
        Ingredient.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Ingredients cleared'))
