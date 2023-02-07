"""
Модели пользователей

Модели:
    CustomUser - пользователь
       Модель пользователя, наследуется от AbstractUser
            Поля:
                email - почта
                username - имя пользователя
                first_name - имя
                last_name - фамилия
                password - пароль
    Subscribe - подписка
         Модель подписки пользователя на другого пользователя
            Поля:
                user - пользователь
                author - автор
            Пользователь не может быть подписан на самого себя

"""


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    """Пользователь"""
    email = models.EmailField(
        'Почта',
        unique=True,
        error_messages={
            'unique': "Пользователь с такой почтой уже существует.",
        },
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        error_messages={
            'unique': "Пользователь с таким именем уже существует.",
        },
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message="Имя пользователя может содержать только буквы, " +
                "цифры и символы @/./+/-/_",
                code='invalid_username',
            ),
        ],
    )
    first_name = models.CharField(
        'Имя',
        max_length=30,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=128,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            ),
        ]

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Подписка"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Пользователь не может быть подписан на ' +
                                  'самого себя')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
