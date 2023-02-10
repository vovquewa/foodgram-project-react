"""
    Сериализаторы для моделей рецептов

    Сериализаторы:
        TagSerializer - сериализатор для тегов
        RecipeGetSerializer - сериализатор для рецептов и метода GET
        RecipePostSerializer - сериализатор для рецептов и методот отличных от GET
        IngredientAmountSerializer - сериализатор для ингредиентов
        IngredientSerializer - сериализатор для ингредиентов
        FollowSerializer - сериализатор для подписок
        
"""

from rest_framework import serializers
from .models import Tag, Recipe, Ingredient
from users.models import Subscribe
from users.serializers import UserSerializer
from recipes.models import IngredientAmount
from drf_extra_fields.fields import Base64ImageField
# Валидатор UniqueTogetherValidator
from rest_framework.validators import UniqueTogetherValidator
# Paginator
from rest_framework.pagination import PageNumberPagination as Paginator
# OrderedDict
from collections import OrderedDict


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов и метода GET

    Выводит только те поля, которые нужны для списка рецептов

    Поля:
        id - id рецепта
        tags - теги рецепта
        author - автор рецепта
            для автора выводятся поля:
                email - email автора
                id - id автора
                username - имя автора
                first_name - имя автора
                last_name - фамилия автора
                is_subscribed - подписан ли текущий пользователь на автора
        ingredients - ингредиенты рецепта
            для ингредиента выводятся поля:
                id - id ингредиента\
                name - название ингредиента
                measurement_unit - единица измерения ингредиента
                amount - количество ингредиента
        is_favorited - добавлен ли рецепт в избранное текущим пользователем
        is_in_shopping_cart - добавлен ли рецепт в список покупок текущим
        пользователем
        name - название рецепта
        image - изображение рецепта
        text - описание рецепта
        cooking_time - время приготовления рецепта
    """

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def get_ingredients(self, obj):
        """
        Возвращает список ингредиентов рецепта
        Используется m2m таблица IngredientAmount



        Поля:
            id - id ингредиента
            name - название ингредиента
            measurement_unit - единица измерения ингредиента
            amount - количество ингредиента
        """

        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            }
            for ingredient in ingredients
        ]

    def get_is_favorited(self, obj):
        """
        Возвращает True, если рецепт добавлен в избранное текущим пользователем
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Возвращает True, если рецепт добавлен в список покупок текущим
        пользователем
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели IngredientAmount
    Поля:
        recipe - рецепт
        id - id ингредиента
        amount - количество ингредиента
    """
    # recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class IngredientRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipePostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe и методов отличных от GET

    Поля:
        ingredients - ингредиенты рецепта
            поля:
                id - id ингредиента
                amount - количество ингредиента
        tags - теги рецепта
            поля:
                id - id тега
        image - изображение рецепта закодированное в base64
        name - название рецепта
        text - описание рецепта
        cooking_time - время приготовления рецепта

    порядок полей при выводе:
        'id',
        'tags',
        'author',
        'ingredients',
        'is_favorited',
        'is_in_shopping_cart',
        'image',
        'name',
        'text',
        'cooking_time'

    порядок полей определяется в методе get_fields


    Все поля обязательны для заполнения
    """
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(max_length=None, use_url=True)
    name = serializers.CharField(max_length=200, required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(min_value=1, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe

# валидаторы
    def validate(self, data):
        """
        Проверка на наличие:
            - ингредиентов
            - тегов
            - картинки
            - названия
            - времени приготовления
        
        Проверка на наличие тегов и ингредиентов в базе
        """
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                'Необходимо указать ингредиенты'
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                'Необходимо указать теги'
            )
        if 'image' not in data:
            raise serializers.ValidationError(
                'Необходимо указать картинку'
            )
        if 'name' not in data:
            raise serializers.ValidationError(
                'Необходимо указать название'
            )
        if 'cooking_time' not in data:
            raise serializers.ValidationError(
                'Необходимо указать время приготовления'
            )
        if not Ingredient.objects.filter(
            id__in=[ingredient['id'] for ingredient in data['ingredients']]
        ).exists():
            raise serializers.ValidationError(
                'Ингредиенты не найдены'
            )
        if not Tag.objects.filter(
            id__in=[tag.id for tag in data['tags']]
        ).exists():
            raise serializers.ValidationError(
                'Теги не найдены'
            )
        return data

    def validate_ingredients(self, value):
        """
        Нельзя добавить один и тот же ингридиент несколько раз
        """
        ingredients = []
        for ingredient in value:
            if ingredient['id'] in ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            ingredients.append(ingredient['id'])
        return value

    def validate_tags(self, value):
        """
        Нельзя добавить один и тот же тег несколько раз
        """
        tags = []
        for tag in value:
            if tag.id in tags:
                raise serializers.ValidationError(
                    'Теги не должны повторяться'
                )
            tags.append(tag.id)

        return value

    def get_is_favorited(self, obj):
        """
        Возвращает True, если рецепт добавлен в избранное текущим пользователем
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Возвращает True, если рецепт добавлен в список покупок текущим
        пользователем
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()

    def create(self, validated_data):
        """
        Создать рецепт
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        """
        Обновить рецепт

        Обязательные поля:
        ingredients - ингредиенты
            id - id ингредиента
            amount - количество ингредиента
        tags - теги (id тега)
        image - изображение закодированное в base64
        name - название рецепта
        text - текст рецепта
        cooking_time - время приготовления
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        for ingredient in ingredients:
            IngredientAmount.objects.update_or_create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                defaults={'amount': ingredient['amount']}
            )
        return instance

    def to_representation(self, instance):
        """
        Переопределение метода to_representation для добавления полей
        ingredients и tags

        Порядок полей в ответе:
        id, tags, author, ingredients, is_favorited, is_in_shopping_cart,
        name, image, text, cooking_time
        """

        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['id'] = instance.id

        representation['ingredients'] = IngredientRecipeGetSerializer(
            IngredientAmount.objects.filter(recipe=instance), many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags, many=True
        ).data

        representation = OrderedDict([
            ('id', representation['id']),
            ('tags', representation['tags']),
            ('author', representation['author']),
            ('ingredients', representation['ingredients']),
            ('is_favorited', representation['is_favorited']),
            ('is_in_shopping_cart', representation['is_in_shopping_cart']),
            ('image', representation['image']),
            ('name', representation['name']),
            ('text', representation['text']),
            ('cooking_time', representation['cooking_time']),
        ])
        return representation


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Recipe для метода GET укороченный

        Поля:
            id - id рецепта
            name - название рецепта
            image - ссылка на изображение рецепта
            cooking_time - время приготовления рецепта

        Сериализатор используется для вывода списка рецептов в сериализаторе
        подпискок пользователя
    """

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscribe

    Возвращает пользователей, на которых подписан текущий пользователь. В
    выдачу добавляются рецепты.

    Параметры запроса:
        page - номер страницы
        limit - количество рецептов на странице
        recipe_limit - количество рецептов в выдаче пользователя

    Поля:
        email - email пользователя
        id - id пользователя
        username - имя пользователя
        first_name - имя пользователя
        last_name - фамилия пользователя
        is_subscribed - подписан ли текущий пользователь на пользователя
        recipes - рецепты пользователя
            поля:
                id - id рецепта
                name - название рецепта
                image - изображение рецепта
                cooking_time - время приготовления рецепта
        recipes_count - количество рецептов пользователя
    """

    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = Subscribe

    def get_is_subscribed(self, obj):
        """
        Проверяет подписан ли текущий пользователь на пользователя

        Возвращает True если подписан, иначе False

        То есть всегда возвращает True, так как мы выводим только тех
        пользователей, на которых подписан текущий пользователь

        """
        return True

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов автора

        Параметры:
            obj - объект пользователя

        Возвращает количество рецептов автора


        """
        queryset = Recipe.objects.filter(author=obj.author)
        return queryset.count()

    def get_recipes(self, obj):
        """
        Метод для получения рецептов авторов на которых подписан пользователь
        C ограничением по количеству согласно параметру запроса recipe_limit

        Параметры:
            obj - объект пользователя

        Возвращает список рецептов пользователя согласно сериализатору
        ShortRecipeSerializer

        """
        request = self.context.get('request')
        quertset = Recipe.objects.filter(author=obj.author)
        limit = request.query_params.get('recipe_limit')
        serializers = ShortRecipeSerializer(
            quertset,
            many=True,
            context={'request': request}
        )
        if limit:
            return serializers.data[:int(limit)]
        return serializers.data
