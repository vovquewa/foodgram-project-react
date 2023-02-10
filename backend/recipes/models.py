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

    Список покупок: ShoppingList:
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


"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.urls import reverse

User = get_user_model()


class Tag(models.Model):
    """Тег"""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цветовой hex-код тега',
        max_length=7,
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
    """Ингредиент"""
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
    """Количество ингредиента"""
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

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class Recipe(models.Model):
    """Рецепт"""
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


class Favorite(models.Model):
    """
        Избранное

        Пользователь может добавить рецепт в избранное
        и убрать его оттуда.
        При этом рецепт может быть добавлен в избранное
        несколькими пользователями.
        При удалении рецепта из избранного он удаляется
        только у текущего пользователя.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingList(models.Model):
    """
        Список покупок

        Модель, которая хранит соответствие между пользователями и рецептами.
        Содержит следующие поля:
            Пользователь: user
            Рецепт: recipe (можно добавить несколько одинаковых рецептов в
            список покупок)
        Связь с моделью Recipe осуществляется через модель Recipe.

        Список рецептов, которые пользователь хочет купить
        вместе с количеством ингредиентов для каждого рецепта.

        Можно добавить рецепт в корзину несколько раз.
        В этом случае при подсчете количества ингредиентов
        для покупки нужно учитывать все добавления рецепта.

        Например, пользователь добавил в корзину рецепт
        с ингредиентами «Сахар - 100 г», «Мука - 200 г»
        и снова добавил этот же рецепт.
        Тогда при подсчете ингредиентов для покупки
        нужно учитывать их сумму, то есть
        «Сахар - 200 г», «Мука - 400 г».

        Пользователь может удалять рецепты из корзины.
        При этом если рецепт был добавлен несколько раз,
        то нужно удалять только одно добавление.

        Например, пользователь добавил в корзину рецепт
        с ингредиентами «Сахар - 100 г», «Мука - 200 г»
        и снова добавил этот же рецепт.
        Потом пользователь удалил одно из добавлений этого рецепта.
        Тогда при подсчете ингредиентов для покупки
        нужно учитывать только одно добавление,
        то есть «Сахар - 100 г», «Мука - 200 г».

        Пользователь может очистить корзину целиком.
        При этом корзина удаляется из базы данных,
        а не очищается.

        Пользователь может просматривать список рецептов,
        которые он добавил в корзину.
        Для каждого рецепта показывается название,
        картинка и время приготовления.

        Пользователь может просматривать список ингредиентов,
        необходимых для приготовления всех рецептов,
        которые он добавил в корзину.
        Ингредиенты должны быть отсортированы по названию
        и группироваться по названию ингредиента.
        Внутри каждой группы ингредиенты должны быть
        отсортированы по названию рецепта.
        В списке должны показываться только те ингредиенты,
        которые есть в рецептах, добавленных в корзину.
        Например, если пользователь добавил в корзину
        рецепт с ингредиентами «Сахар - 100 г», «Мука - 200 г»,
        а потом удалил этот рецепт из корзины,
        то в списке ингредиентов не должно быть
        «Сахар - 100 г», «Мука - 200 г».

    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        help_text='Пользователь, который добавил рецепт в корзину',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
        help_text='Рецепт, который добавлен в корзину',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
