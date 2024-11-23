from enum import Enum

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract_models import BaseCategoryGenreModel, BaseReviewCommentModel
from .validators import CurrentYearMaxValueValidator


USERNAME_FIELD_SIZE = 150
EMAIL_FIELD_SIZE = 254


class RoleChoices(str, Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    @classmethod
    def choices(cls):
        return [
            (cls.USER.value, _('user')),
            (cls.MODERATOR.value, _('moderator')),
            (cls.ADMIN.value, _('admin')),
        ]

    @classmethod
    def max_length(cls):
        return max(len(role) for role in cls)


class User(AbstractUser):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message=(
            'Username may contain only letters,'
            ' digits, and @/./+/-/_ characters.'
        )
    )

    username = models.CharField(
        max_length=USERNAME_FIELD_SIZE,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    email = models.EmailField(unique=True, max_length=EMAIL_FIELD_SIZE)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=RoleChoices.max_length(),
        choices=RoleChoices.choices(),
        default=RoleChoices.USER
    )

    @property
    def is_admin(self):
        return (self.role == RoleChoices.ADMIN
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == RoleChoices.MODERATOR


class Category(BaseCategoryGenreModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseCategoryGenreModel):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        verbose_name='Год создания',
        validators=[
            CurrentYearMaxValueValidator(
                message='Год не может быть больше, чем сейчас')]
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

    def __str__(self):
        return self.name


class Review(BaseReviewCommentModel):
    title = models.ForeignKey(
        'reviews.Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(
                settings.MAX_SCORE,
                f'Оценка не может быть выше {settings.MAX_SCORE}'
            ),
            MinValueValidator(
                settings.MIN_SCORE,
                f'Оценка не может быть ниже {settings.MIN_SCORE}'
            )
        ],
        verbose_name='Оценка'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            ),
        )


class Comment(BaseReviewCommentModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
