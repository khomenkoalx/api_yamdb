from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .abstract_models import BaseModel
from .validators import CurrentYearMaxValueValidator

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


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.IntegerField(
        null=True,
        validators=[
            MaxValueValidator(10, message='Оценка должна быть не выше 10'),
            MinValueValidator(1, message='Оценка должна быть не ниже 1')
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'],
                                    name='unique_review')
        ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:15]
