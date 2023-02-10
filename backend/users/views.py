"""
Вьюхи и вьюсеты для модели User

Вьюсеты позволяют управлять поведением API, например, определять
методы, которые будут доступны для каждого маршрута.

Вьюсеты:
    CustomUserViewSet - вьюсет для модели User
"""


from django.shortcuts import render
from rest_framework import viewsets
from .models import CustomUser, Subscribe
from .serializers import UserSerializer
from recipes.serializers import SubscribeSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from api.pagination import CustomPageNumberPagination
# permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# get_paginated_response


from rest_framework.decorators import action
# status
from rest_framework import status
# get_user_model
from django.contrib.auth import get_user_model
# get_object_or_404
from rest_framework.generics import get_object_or_404

User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """
    Вьюсет для модели User
    """
    pagination_class = CustomPageNumberPagination
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """
            Метод позволяющий подписаться или отписаться на автора

            POST - подписаться
            DELETE - отписаться

            Возвращает статус 201 при успешной подписке
            Возвращает статус 204 при успешной отписке

            Возвращает статус 400 при попытке подписаться на себя
            Возвращает статус 400 если пользователь уже подписан на автора
            Возвращает статус 404 при попытке подписаться на несуществующего
            пользователя
            Возваращает статус 401 при попытке подписаться неавторизованным
            пользователем

            Метод доступен только авторизованным пользователям

            Метод работает по адресу /api/users/{id}/subscribe/

        """
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'error': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if Subscribe.objects.filter(user=user, author=author).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.get_or_create(user=user, author=author)
            return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Subscribe.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)