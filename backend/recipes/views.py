from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter

from .models import (
    Tag, Recipe, Ingredient, Favorite, ShoppingList, IngredientAmount
)
from .serializers import (
    TagSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    IngredientSerializer,
    ShortRecipeSerializer
)
from api.pagination import CustomPageNumberPagination
from .filters import RecipeFilter, IngredientFilter

# action decorator
from rest_framework.decorators import action
# get_object_or_404
from rest_framework.generics import get_object_or_404
# IsAuthenticated permission
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAuthorOrReadOnly
# Response
from rest_framework.response import Response
# status
from rest_framework import status
# Sum
from django.db.models import Sum
# HttpResponce
from django.http import HttpResponse
# ApiView
from rest_framework.views import APIView


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
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """
        Переопределение метода get_queryset

        Необходимо для того, чтобы возвращался список рецептов, с 
        использования фильтров:
        - author - id автора
        - tags - список тегов (по slug)
        - is_favorited - 1 - показывать только избранные рецепты
        - is_in_shopping_cart - 1 - показывать только рецепты, которые
        находятся в списке покупок

        :return: QuerySet

        """
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')

        if author:
            queryset = queryset.filter(author__id=author)
            return queryset
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)
            return queryset
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def get_permissions(self):
        """
        Права доступа для методов

        Для GET, HEAD, OPTIONS - доступно всем пользователям
        Для POST - доступно только авторизованным пользователям
        Для DELETE, PUT, PATCH - доступно только автору рецепта
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthorOrReadOnly]
        self.permission_classes = [AllowAny]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        """
        Удаление рецепта

        :param request: запрос
        :param args: аргументы
        :param kwargs: ключевые аргументы
        :return: Response

        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            'Рецепт успешно удален',
            status=status.HTTP_204_NO_CONTENT
        )

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
            return Response(
                    {'success': 'Рецепт успешно добавлен в избранное'},
                    status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(
                    {'success': 'Рецепт успешно удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT
                )

    # метод для добавление рецепта в список покупок
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """
        Добавление и удаление рецепта из списка покупок

        POST /api/recipes/{id}/shopping_cart/ - добавление рецепта в список
        покупок
        DELETE /api/recipes/{id}/shopping_cart/ - удаление рецепта из списка
        покупок

        Возвращает статус 201 при успешном добавлении в список покупок
        Возвращает статус 204 при успешном удалении из списка покупок

        Возвращает статус 400 при неверном запросе
            Когда рецепт уже есть в списке покупок при добавлении
            Когда рецепта не существует при добавлении
            Когда рецепта нет в списке покупок при удалении

        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': 'Рецепт уже есть в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingList.objects.get_or_create(user=user, recipe=recipe)
            data = ShortRecipeSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not ShoppingList.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(
                    {'error': 'Рецепта нет в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingList.objects.filter(user=user, recipe=recipe).delete()
            return Response(
                {'success': 'Рецепт удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT
            )
# вью функция для получения списка покупок в формате pdf


class DownloadShoppingCartView(APIView):
    """
    Возвращает список покупок в формате txt

    GET /api/download_shopping_cart/ - возвращает список покупок в формате txt

    Вид списка покупок:
        Название ингредиента - количество, единица измерения

    Пример списка покупок:
        Сахар - 100 г
        Молоко - 1 л

    Возвращает статус 200 при успешном получении списка покупок
    Возвращает статус 400 при неверном запросе
        Когда список покупок пуст

    декоратор @api_view(['GET']) - означает, что функция принимает только GET
    запросы и возвращает только ответы в формате json. Декоратор прописывается
    в url.py в urlpatterns в виде: path('download_shopping_cart/',
    download_shopping_cart, name='download_shopping_cart'),
    """

    def get_permissions(self):
        """
        Переопределяем метод get_permissions, чтобы разрешить доступ
        только аутентифицированным пользователям

        Иначе будет ошибка:
            AttributeError: 'AnonymousUser' object has no attribute
            'is_authenticated'

        Разрешены методы только GET
        """
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return []

    def get(self, request):
        user = request.user
        shopping_list = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount')).order_by('ingredient__name')
        if not shopping_list:
            return Response(
                {'error': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_list = [
            f'{item["ingredient__name"]} - {item["total_amount"]}' +
            f' {item["ingredient__measurement_unit"]}'
            for item in shopping_list
        ]
        shopping_list = '\r'.join(shopping_list)
        response = HttpResponse(shopping_list, content_type='text/plain')
        # response['Content-Disposition'] = 'attachment;
        # filename="shopping_list.txt"'
        response['Content-Disposition'] = (
             'attachment; filename="shopping_list.txt"'
        )
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Ingredient
    Список ингредиентов с возможностью поиска по имени вначале строки
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter
