from django.contrib.auth import get_user_model
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


class Title(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True
    )


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        related_name='genres',
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        related_name='genres',
        on_delete=models.CASCADE
    )


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    author = models.IntegerField()
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    author = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)
