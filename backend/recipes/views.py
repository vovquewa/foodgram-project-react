"""
    Вьюхи и вьюсеты для приложения рецептов

    Вьюхи:

    Вьюсеты:
        TagViewSet - вьюсет для модели Tag
        RecipeViewSet - вьюсет для модели Recipe
        IngredientViewSet - вьюсет для модели Ingredient
"""

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter

from .models import Tag, Recipe, Ingredient, Favorite
from .serializers import (
    TagSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    IngredientSerializer
)
from api.pagination import CustomPageNumberPagination
from .filters import RecipeFilter

# action decorator
from rest_framework.decorators import action
# get_object_or_404
from rest_framework.generics import get_object_or_404
# IsAuthenticated permission
from rest_framework.permissions import IsAuthenticated
# Response
from rest_framework.response import Response
# status
from rest_framework import status


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Tag
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Recipe
    """
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    # метод для добавление рецепта в избранное
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """
        Добавление рецепта в избранное

        POST /api/recipes/{id}/favorite/ - добавление рецепта в избранное
        DELETE /api/recipes/{id}/favorite/ - удаление рецепта из избранного

        Возвращает статус 201 при успешном добавлении в избранное
        Возвращает статус 204 при успешном удалении из избранного

        Возвращает статус 400 при неверном запросе
            Когда рецепт уже есть в избранном при добавлении
            Когда рецепта не существует при добавлении
            Когда рецепта нет в избранном при удалении

        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': 'Рецепт уже есть в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Ingredient
    Список ингредиентов с возможностью поиска по имени вначале строки
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)
