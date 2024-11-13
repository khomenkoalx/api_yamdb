from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum


class RoleChoices(Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)
    bio = models.TextField(max_length=150, blank=True)
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices(),
        default=RoleChoices.USER.value
    )

    @property
    def is_admin(self):
        return self.role == RoleChoices.ADMIN.value or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == RoleChoices.MODERATOR.value
