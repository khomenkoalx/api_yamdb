from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.SmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=0,
                message='Введен слишком маленький год'
            ),
            MaxValueValidator(
                limit_value=timezone.now().year,
                message='Год не может быть больше, чем сейчас')]
    )
    description = models.TextField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    @property
    def rating(self):
        reviews = self.reviews.aggregate(Avg('score'))
        return reviews['score__avg']

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        related_name='genres',
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return f'{self.title} - {self.genre}'

    class Meta:
        unique_together = ('title', 'genre')


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
