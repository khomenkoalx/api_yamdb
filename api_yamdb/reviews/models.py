from enum import Enum

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from .constants import (
    USERNAME_FIELD_SIZE,
    EMAIL_FIELD_SIZE,
    MIN_SCORE,
    MAX_SCORE,
    MAX_STR_LENGTH,
    NAME_MAX_LENGTH
)


def validate_year(year):
    if year > timezone.now().year:
        raise ValidationError(
            f'Год не может быть больше текущего - '
            f'{timezone.now().year}, Вы ввели {year}.'
        )
    return year


def validate_myself(username):
    if username == settings.MYSELF_NAME:
        raise ValidationError(
            f'Имя пользователя не может быть "{settings.MYSELF_NAME}".'
        )
    return username


class RoleChoices(str, Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    @classmethod
    def choices(cls):
        return [
            ('user', 'пользователь'),
            ('moderator', 'модератор'),
            ('admin', 'администратор')
        ]

    @classmethod
    def max_length(cls):
        return max(len(role.value) for role in cls)


class User(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_FIELD_SIZE,
        unique=True,
        validators=[
            RegexValidator(regex=settings.USERNAME_REGEX),
            validate_myself
        ],
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_FIELD_SIZE,
        verbose_name='Email')
    bio = models.TextField(blank=True, verbose_name='Биография')
    role = models.CharField(
        max_length=RoleChoices.max_length(),
        choices=RoleChoices.choices(),
        default=RoleChoices.USER,
        verbose_name='Роль'
    )

    @property
    def is_admin(self):
        return self.role == RoleChoices.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == RoleChoices.MODERATOR

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class BaseNameSlugModel(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        abstract = True
        ordering = ('-name',)

    def __str__(self):
        return self.slug


class BasePostModel(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='%(class)ss'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:MAX_STR_LENGTH]


class Category(BaseNameSlugModel):
    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNameSlugModel):
    class Meta(BaseNameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        verbose_name='Год создания',
        validators=[validate_year]
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', '-name',)

    def __str__(self):
        return f'Произведение {self.name[:MAX_STR_LENGTH]}, {self.year} года.'


class Review(BasePostModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(
                MAX_SCORE,
                f'Оценка не может быть выше {MIN_SCORE}'
            ),
            MinValueValidator(
                MIN_SCORE,
                f'Оценка не может быть ниже {MIN_SCORE}'
            )
        ],
        verbose_name='Оценка'
    )

    class Meta(BasePostModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            ),
        )


class Comment(BasePostModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta(BasePostModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
