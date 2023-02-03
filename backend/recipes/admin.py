from django.contrib import admin
from .models import Recipe, Ingredient, Tag, IngredientAmount


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'image',
        'ingredients_custom',
        'tags_custom',
        'cooking_time',
        'pub_date',
    )
    list_filter = ('author', 'name', 'tags', 'pub_date')
    search_fields = ('name', 'text', 'ingredients', 'tags')
    empty_value_display = '-пусто-'

    def ingredients_custom(self, obj):
        return ", ".join([str(p) for p in obj.ingredients.all()])
    ingredients_custom.short_description = 'Ингредиенты'

    def tags_custom(self, obj):
        return ", ".join([str(p) for p in obj.tags.all()])
    tags_custom.short_description = 'Теги'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(IngredientAmount)
