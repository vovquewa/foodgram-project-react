"""
Описание маршрутов для API

Все маршруты, которые начинаются с /api/ будут обрабатываться этим файлом.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.serializers import UserSerializer
from users.views import CustomUserViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
