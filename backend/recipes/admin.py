from django.contrib import admin
from django.conf import settings
from .models import (
    Recipe,
    Ingredient,
    Tag,
    IngredientAmount,
    Favorite,
    ShoppingList,
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'image',
        'ingredients_custom',
        'tags_custom',
        'favorites_count',
        'cooking_time',
        'pub_date',
    )
    list_filter = ('author', 'name', 'tags', 'pub_date')
    search_fields = ('name', 'text', 'ingredients', 'tags')
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('-pub_date',)

    def ingredients_custom(self, obj):
        return ", ".join([str(p) for p in obj.ingredients.all()])
    ingredients_custom.short_description = 'Ингредиенты'

    def tags_custom(self, obj):
        return ", ".join([str(p) for p in obj.tags.all()])
    tags_custom.short_description = 'Теги'

    # количество добавлений рецепта в избранное
    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    favorites_count.short_description = 'Количество добавлений в избранное'


# Ингридиенты
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('-id',)


# Теги
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('name',)}


# Ингридиенты в рецепте
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    list_filter = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient', 'amount')
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('recipe', '-id')


# Избранное
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('-id',)
    list_display_links = ('id', 'user', 'recipe')


# Списко покупок
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('-id',)
    list_display_links = ('id', 'user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
