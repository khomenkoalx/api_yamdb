from rest_framework import serializers
from .models import User


class SignUpSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        error_messages={"invalid": "Недопустимые символы в имени пользователя."},
        required=True
    )
    email = serializers.EmailField(
        max_length=254,
        error_messages={
            "max_length": "Email не может быть длиннее 254 символов."
        },
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя 'me' использовать нельзя.")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserMeProfileSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=False,
        error_messages={
            "invalid": "Имя пользователя содержит недопустимые символы."
        }
    )
    email = serializers.EmailField(
        max_length=254,
        required=False,
        error_messages={
            "max_length": "Email не может быть длиннее 254 символов."
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('email', 'role')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
