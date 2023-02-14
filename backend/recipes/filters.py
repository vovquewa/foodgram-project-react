"""
Филтры для рецептов

Фильтры для рецептов, которые используются во вьюхах

Фильтры:
    - RecipeFilter: фильтр для рецептов
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    - IngredientFilter: фильтр для ингредиентов
    Доступна фильтрация по названию ингредиента.
    Доступен поиск по названию ингредиента.



"""
from django.contrib.auth import get_user_model
from django_filters import (FilterSet, NumberFilter,
                            ModelChoiceFilter, ModelMultipleChoiceFilter,
                            CharFilter,
                            )
from .models import Recipe, Ingredient, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов

    Фильтры:
    is_favorited
        integer
        Enum: 0 1
        Показывать только рецепты, находящиеся в списке избранного.

    is_in_shopping_cart
        integer
        Enum: 0 1
        Показывать только рецепты, находящиеся в списке покупок.
    author
        integer
        Показывать рецепты только автора с указанным id.
    tags
        Array of strings
        Example: tags=lunch&tags=breakfast
        Показывать рецепты только с указанными тегами (по slug)
    """

    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')
    author = NumberFilter(method='filter_author')
    # author = ModelChoiceFilter(
    #     field_name='author__id',
    #     to_field_name='id',
    #     queryset=User.objects.all()
    # )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            if self.request.user.is_authenticated:
                return queryset.filter(favorites__user=self.request.user)
            else:
                return queryset.none()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            if self.request.user.is_authenticated:
                return queryset.filter(shopping_cart__user=self.request.user)
            else:
                return queryset.none()
        return queryset

    def filter_tags(self, queryset, name, value):
        """
        Фильтр по тегам
        """
        return queryset.filter(tags__slug__in=value)

    def filter_author(self, queryset, name, value):
        """
        Фильтр по id автора
        """
        return queryset.filter(author__id=value)

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )


class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')