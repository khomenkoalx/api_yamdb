from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment
from reviews.models import User, USERNAME_FIELD_SIZE, EMAIL_FIELD_SIZE

MYSELF_NAME = 'me'
CONFORMATION_CODE_SIZE = 128


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
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        read_only_fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


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
        max_value=settings.MAX_SCORE,
        error_messages={
            'min_value': f'Оценка должна быть не ниже {settings.MIN_SCORE}',
            'max_value': f'Оценка должна быть не выше {settings.MAX_SCORE}'
        }
    )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        author = self.context['request'].user
        title_id = self.context['request'].parser_context['kwargs'].get(
            'title_id'
        )
        title = get_object_or_404(Title, id=title_id)

        if title.reviews.filter(author=author).exists():
            raise serializers.ValidationError(
                f'Отзыв на произведение "{title.name}" уже существует'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        read_only_fields = ('author', 'pub_date', 'title')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        read_only_fields = ('author', 'pub_date', 'review')


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
