from django.db import models


class BaseModel(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        abstract = True
        verbose_name = 'Общая модель'
        verbose_name_plural = 'Общие модели'

    def __str__(self):
        return self.slug


class BaseReviewComment(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        abstract = True