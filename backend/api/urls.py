"""
Описание маршрутов для API

Все маршруты, которые начинаются с /api/ будут обрабатываться этим файлом.

Версия 1:
    /api/users/ - список пользователей
    /api/users/<id> - детали пользователя
    /api/auth/ - авторизация

    /api/tags/ - список тегов
    /api/tags/<id> - детали тега

    /api/recipes/ - список рецептов
    /api/recipes/<id> - детали рецепта

    /api/ingredients/ - список ингредиентов
    /api/ingredients/<id> - детали ингредиента

"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet
from recipes.views import TagViewSet, RecipeViewSet, IngredientViewSet


app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
