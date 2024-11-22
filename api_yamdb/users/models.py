from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

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
