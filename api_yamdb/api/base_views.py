from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    ListModelMixin,
    DestroyModelMixin,
    CreateModelMixin
)
from rest_framework import viewsets

from .permissions import IsAdminUserOrReadOnly


class SearchableViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)
