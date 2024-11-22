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
