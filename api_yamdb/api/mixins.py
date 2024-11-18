from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    ListModelMixin,
    DestroyModelMixin,
    CreateModelMixin
)

from .permissions import IsAdminOrReadOnly


class SearchableViewSet(
    viewsets.GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin
):
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
