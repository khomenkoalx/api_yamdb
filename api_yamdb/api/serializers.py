from django.conf import settings
from rest_framework import serializers

from .constants import CONFIRMATION_CODE_SIZE
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment,
    User,
    USERNAME_FIELD_SIZE,
    EMAIL_FIELD_SIZE,
    is_valid_username
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
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        read_only_fields = fields


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
        return TitleSafeSerializer(instance).data

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
        if Review.objects.filter(title_id=title_id, author=author).exists():
            raise serializers.ValidationError(
                f'Отзыв на произведение '
                f'\'{Title.objects.get(id=title_id).name}\'уже существует'
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
        max_length=USERNAME_FIELD_SIZE,
        validators=[is_valid_username]
    )
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_SIZE,
        required=True
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=USERNAME_FIELD_SIZE,
        regex=settings.USERNAME_REGEX,
        required=True,
        validators=[is_valid_username]
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_SIZE,
        required=True,
    )


class UserSerializer(serializers.ModelSerializer):

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

    def validate(self, user):
        if 'username' in user:
            username = user['username']
            is_valid_username(username)
        return user
