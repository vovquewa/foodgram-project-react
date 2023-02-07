# Кастомная форма для регистрации пользователя
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name')
