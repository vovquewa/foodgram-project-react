"""
Вьюхи и вьюсеты для модели User

Вьюсеты позволяют управлять поведением API, например, определять
методы, которые будут доступны для каждого маршрута.

Вьюсеты:
    CustomUserViewSet - вьюсет для модели User
"""

from django.shortcuts import render
from rest_framework import viewsets
from .models import CustomUser
from .serializers import UserSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from api.pagination import CustomPageNumberPagination


class CustomUserViewSet(DjoserUserViewSet):
    """
    Вьюсет для модели User
    """
    pagination_class = CustomPageNumberPagination
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
