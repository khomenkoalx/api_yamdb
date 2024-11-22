from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .abstract_models import BaseModel, BaseReviewComment
from .validators import CurrentYearMaxValueValidator
from .constants import MIN_SCORE, MAX_SCORE


User = get_user_model()


class Category(BaseModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseModel):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=255,
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

    def __str__(self):
        return self.name


class Review(BaseReviewComment):
    title = models.ForeignKey(
        'reviews.Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(MAX_SCORE, f'Оценка не может быть выше {MAX_SCORE}'),
            MinValueValidator(MIN_SCORE, f'Оценка не может быть ниже {MIN_SCORE}')
        ],
        verbose_name='Оценка'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            ),
        )


class Comment(BaseReviewComment):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
