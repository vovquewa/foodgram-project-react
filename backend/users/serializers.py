"""
Сериализаторы для моделей приложения users

Сериализаторы используются для преобразования данных из базы данных в JSON

и обратно. Сериализаторы позволяют управлять тем, какие поля будут включены в

ответы API, как они будут названы и как будут отображаться в JSON.

Сериализаторы также позволяют валидировать входящие данные, чтобы убедиться,

что они соответствуют ожиданиям.


Сериализаторы:
    UserSerializer - сериализатор для модели User
    UserCreateSerializer - сериализатор для создания нового пользователя
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer as UCS
from .models import Subscribe
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    # Добавляем поле is_subscribed, которое будет возвращать True, если
    # пользователь подписан на автора, и False, если нет
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    # Переопределяем метод для сериализации поля is_subscribed
    def get_is_subscribed(self, obj):
        # Возвращаем True, если пользователь подписан на автора, иначе False
        if self.context['request'].user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=self.context['request'].user,
            author=obj
        ).exists()


class UserCreateSerializer(UCS):
    """Сериализатор для создания нового пользователя"""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta(UCS.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    # Переопределяем метод для валидации поля password
    def validate_password(self, value):
        """
        Валидация пароля
        """
        try:
            validate_password(value)
        except ValidationError as err:
            raise serializers.ValidationError(
                _('Пароль не соответствует требованиям безопасности')
            )
        return value

    # Переопределяем метод для валидации поля email
    def validate_email(self, value):
        # Проверяем, что email не занят
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _('Пользователь с таким email уже существует')
            )
        return value

    # Переопределяем метод для валидации поля username
    def validate_username(self, value):
        # Проверяем, что username не занят
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                _('Пользователь с таким username уже существует')
            )
        return value
