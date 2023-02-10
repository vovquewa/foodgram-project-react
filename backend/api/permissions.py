"""
Права доступа к API
"""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Права доступа для автора и для всех остальных
    """

    def has_object_permission(self, request, view, obj):
        """
        Права доступа для автора и для всех остальных
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Права доступа для автора для модели списка покупок

        Для методов:
            - DELETE

        Только автор списка покупок может удалить список покупок
        """
        if request.method == 'DELETE':
            return obj.user == request.user

        return True
