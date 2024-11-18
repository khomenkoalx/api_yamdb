from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, Genre, Title, Review
from .filters import TitleFilter
from .mixins import SearchableViewSet
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSafeSerializer,
    TitleSerializer,
    ReviewSerializer
)
from .permissions import IsAdminOrReadOnly


class CategoryViewSet(SearchableViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(SearchableViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleSafeSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
