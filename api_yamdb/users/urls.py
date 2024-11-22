from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import signup, get_token, me, UserViewSet

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/users/me/', me, name='me'),
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', get_token, name='token'),
]
