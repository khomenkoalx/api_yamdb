from rest_framework import serializers
from .models import User, USERNAME_FIELD_SIZE, EMAIL_FIELD_SIZE

MYSELF_NAME = 'me'
CONFORMATION_CODE_SIZE = 128


class SignUpSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=USERNAME_FIELD_SIZE,
        error_messages={
            'invalid': 'Недопустимые символы в имени пользователя.'
        },
        required=True
    )
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_SIZE,
        required=True
    )

    def validate_username(self, username):
        if username == MYSELF_NAME:
            raise serializers.ValidationError(
                f'Имя \'{MYSELF_NAME}\' использовать нельзя.'
            )
        return username


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_FIELD_SIZE,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=CONFORMATION_CODE_SIZE,
        required=True,
    )

    def validate_username(self, username):
        if username == MYSELF_NAME:
            raise serializers.ValidationError(
                f'Имя \'{MYSELF_NAME}\' использовать нельзя.'
            )
        return username


class BaseUserSerializer:
    _are_required = False
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=USERNAME_FIELD_SIZE,
        required=_are_required,
        error_messages={
            'invalid': 'Имя пользователя содержит недопустимые символы.'
        }
    )
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_SIZE,
        required=_are_required,
        error_messages={
            'max_length': 'Email не может быть длиннее 254 символов.'
        }
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class UserMeProfileSerializer(serializers.ModelSerializer, BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('role',)


class UserSerializer(serializers.ModelSerializer, BaseUserSerializer):
    BaseUserSerializer._are_required = True
