from rest_framework import routers
from django.urls import path, include
from .views import CategoryViewSet

v1_router = routers.DefaultRouter()
v1_router.register(r'categories', CategoryViewSet, basename='categoires')

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
