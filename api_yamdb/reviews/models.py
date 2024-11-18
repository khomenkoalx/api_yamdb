from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.SmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=0,
                message='Введен слишком маленький год'
            ),
            MaxValueValidator(
                limit_value=lambda: timezone.now().year,
                message='Год не может быть больше, чем сейчас')]
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        related_name='genres',
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


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE) # TODO - поменять на ссылку на пользователя (on_delete=models.CASCADE)
    score = models.SmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Значение должно быть больше ноля'
            ),
            MaxValueValidator(
                limit_value=10,
                message='Значение должно быть не больше десяти'
            )
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[15:]


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
        return self.text[15:]
