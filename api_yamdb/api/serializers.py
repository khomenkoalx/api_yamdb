import re

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.constants import TITLE_READ_ONLY_FIELDS, CONFORMATION_CODE_SIZE
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment,
    RoleChoices,
    User,
    USERNAME_FIELD_SIZE,
    EMAIL_FIELD_SIZE
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSafeSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.ReadOnlyField()

    class Meta:
        model = Title
        fields = TITLE_READ_ONLY_FIELDS
        read_only_fields = TITLE_READ_ONLY_FIELDS


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    def to_representation(self, instance):
        if instance:
            serializer = TitleSafeSerializer(instance)
            return serializer.data
        return {}

    class Meta:
        model = Title
        fields = (
            'name',
            'year',
            'description',
            'genre',
            'category',
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(
        min_value=settings.MIN_SCORE,
        max_value=settings.MAX_SCORE
    )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        author = self.context['request'].user
        title_id = self.context['request'].parser_context['kwargs']['title_id']

        title = get_object_or_404(Title, id=title_id)

        if title.reviews.filter(author=author).exists():
            raise serializers.ValidationError(
                f'Отзыв на произведение "{title.name}" уже существует'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_FIELD_SIZE
    )
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_SIZE,
        required=True
    )

    def validate(self, instance):
        if instance['username'] == settings.MYSELF_NAME:
            raise serializers.ValidationError(
                f'Имя \'{settings.MYSELF_NAME}\' использовать нельзя.'
            )
        if len(instance['username']) > USERNAME_FIELD_SIZE:
            raise serializers.ValidationError(
                f'Имя пользователя не может быть '
                f'длиннее {USERNAME_FIELD_SIZE} символов.'
            )
        if not re.match(r'^[\w.@+-]+\Z', instance['username']):
            raise serializers.ValidationError(
                'Имя пользователя должно содержать только буквы, цифры, '
                'точки, подчеркивания, а также символы @, +, -, и .'
            )
        errors = {
            'username': User.objects.filter(
                username=instance['username']
            ).exists(),
            'email': User.objects.filter(email=instance['email']).exists(),
        }

        if errors['username'] ^ errors['email']:
            field = 'username' if errors['username'] else 'email'
            raise serializers.ValidationError(
                f"Пользователь с {field} {instance[field]} уже существует."
            )

        return instance


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=USERNAME_FIELD_SIZE,
        regex=r'^[\w.@+-]+\Z',
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=CONFORMATION_CODE_SIZE,
        required=True,
    )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=USERNAME_FIELD_SIZE,
    )
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_SIZE
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

    def validate(self, instance):
        if instance.get('username'):
            if instance['username'] == settings.MYSELF_NAME:
                raise serializers.ValidationError(
                    f'Имя {settings.MYSELF_NAME} использовать нельзя.'
                )
            if len(instance['username']) > USERNAME_FIELD_SIZE:
                raise serializers.ValidationError(
                    f'Имя пользователя не может быть '
                    f'длиннее {USERNAME_FIELD_SIZE} символов.'
                )
            if not re.match(r'^[\w.@+-]+\Z', instance['username']):
                raise serializers.ValidationError(
                    'Имя пользователя должно содержать только буквы, цифры, '
                    'точки, подчеркивания, а также символы @, +, -, и .'
                )
        if instance.get('email'):
            if User.objects.filter(email=instance['email']).exists():
                raise serializers.ValidationError(
                    f'Пользователь с email {instance["email"]} уже существует.'
                )
        if instance.get('username'):
            if User.objects.filter(username=instance['username']).exists():
                raise serializers.ValidationError(
                    f'Пользователь с именем {instance["username"]} '
                    f'уже существует.'
                )
        if instance.get('role') and instance['role'] not in (
            [role[0] for role in RoleChoices.choices()]
        ):
            raise serializers.ValidationError(
                f'Указанное {instance["role"]} для поля '
                f'"role" не является допустимым.'
            )
        return instance
