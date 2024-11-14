from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from reviews.models import Category, Genre, Title
from .serializers import CategorySerializer, GenreSerializer, TitleSafeSerializer, TitleSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleSafeSerializer
        return TitleSerializer
