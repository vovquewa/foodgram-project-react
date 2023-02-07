from django.contrib import admin
from django.conf import settings
from .models import CustomUser, Subscribe
from .forms import CustomUserCreationForm


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'username',
        'first_name',
        'last_name'
        )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    form = CustomUserCreationForm
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('-id',)


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
    )
    list_filter = (
        'user',
        'author'
        )
    search_fields = (
        'user',
        'author'
        )
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    ordering = ('-id',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)