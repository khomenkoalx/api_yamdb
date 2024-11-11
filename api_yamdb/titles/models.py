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
    category = models.ForeignKey(Category, related_name='titles')


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, related_name='genres')
    genre = models.ForeignKey(Genre, related_name='genres')


class Review(models.Model):
    title = models.ForeignKey(Title, related_name='reviews')
    text = models.TextField()


class Comment(models.Model):
    review = models.ForeignKey(Review, related_name='comments')
    text = models.TextField()
