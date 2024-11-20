from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import AuthViewSet, UserViewSet

v1_router = DefaultRouter()
v1_router.register(r'auth', AuthViewSet, basename='auth')
v1_router.register(r'users', UserViewSet, basename='users')
urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
