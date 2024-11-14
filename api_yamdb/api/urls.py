from rest_framework import routers
from django.urls import path, include
from .views import CategoryViewSet, GenreViewSet

v1_router = routers.DefaultRouter()
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(r'genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
