"""
Модели приложения recipes.

Модели:
    Рецепт: Recipe
        Основная модель приложения, которая описывает рецепт.
        Содержит следующие поля:
            Автор публикации: author (модель User описана в модуле users)
            Название рецепта: name
            Изображение рецепта: image
            Текстовое описание рецепта: text
            Ингредиенты: ingredients
            Теги: tags (можно установить несколько тегов на один рецепт, выбор
            из предустановленных)
            Время приготовления в минутах: cooking_time
        Все поля обязательны для заполнения.

    Ингредиент: Ingredient
        Модель, которая хранит данные об ингридиентах.
        Данные об ингридиентах хранятся в нескольких связанных таблицах.
        Содержит следующие поля:
            Название ингредиента: name  (уникальное)
            Единица измерения: measurement_unit
        Все поля обязательны для заполнения.
        Связь с моделью Recipe осуществляется через модель
        IngredientAmount.

    Тег: Tag
        Модель содержащяя список тегов, которые можно установить на рецепт.
        Содержит следующие поля:
            Название тега: name (уникальное)
            Цветовой hex-код тега: color
            Служебное название тега: slug
            Связь с моделью Recipe осуществляется через модель TagRecipe.

    Список покупок: ShoppingCart:
        Модель, которая хранит соответствие между пользователями и рецептами.
        Содержит следующие поля:
            Пользователь: user
            Рецепт: recipe (можно добавить несколько одинаковых рецептов в
            список покупок)
        Связь с моделью Recipe осуществляется через модель Recipe.

    Избранное: Favorite:
        Модель, которая хранит избранные рецепты пользователей.
        Содержит следующие поля:
            Пользователь: user
            Рецепт: recipe (можно добавить несколько рецептов в избранное)
        Связь с моделью Recipe осуществляется через модель Recipe.

    Подписки: Subscribe:
        Модель, которая хранит подписки пользователей на авторов рецептов.
        Содержит следующие поля:


"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цветовой hex-код тега',
        max_length=7,
        unique=True,
        default='#000000',
        validators=[RegexValidator(
            regex=r'^#[0-9a-fA-F]{6}$',
            message='Введите корректный цветовой hex-код'
        )]
    )
    slug = models.SlugField(
        verbose_name='Служебное название тега',
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        unique=True
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['ingredient']
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_amount'
            )
        ]
        db_table = 'ingredient_amount'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Введите положительное число')]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipe', kwargs={'recipe_id': self.id})
