from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.permissions import SAFE_METHODS

from reviews.models import Category, Genre, Title, Review
from .filters import TitleFilter
from .mixins import SearchableViewSet
from .permissions import (IsAdminModeratorAuthorOrReadOnly,
                          IsAdminUserOrReadOnly)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSafeSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
)


class CategoryViewSet(SearchableViewSet, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(SearchableViewSet, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminUserOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleSafeSerializer
        return TitleSerializer

    def get_queryset(self):
        titles = Title.objects.prefetch_related(
            'reviews').annotate(
                rating=Avg('reviews__score')
        )
        return titles


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        serializer.save(
            author=self.request.user,
            review=review
        )
