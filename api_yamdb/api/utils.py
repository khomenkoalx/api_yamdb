import re

from rest_framework import serializers
from django.conf import settings


def is_valid_user(username: str):
    if username == settings.MYSELF_NAME:
        raise serializers.ValidationError(
            f'Имя \'{settings.MYSELF_NAME}\' использовать нельзя.'
        )
    if not re.match(settings.USERNAME_REGEX, username):
        raise serializers.ValidationError(
            'Имя пользователя должно содержать только буквы, цифры, '
            'точки, подчеркивания, а также символы @, +, -, и .'
        )
