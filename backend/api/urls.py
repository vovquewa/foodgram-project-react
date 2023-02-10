from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet
from recipes.views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    DownloadShoppingCartView
)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartView.as_view(),
        name='download_shopping_cart'
    ),
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
