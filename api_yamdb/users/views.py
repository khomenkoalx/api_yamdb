from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import SignUpSerializer
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username']
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            'admin@yamdb.com',
            [user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='token')
    def get_token(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            return Response({"detail": "Неверный код подтверждения"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = AccessToken.for_user(user)
        return Response({
            'access': str(access_token),
        }, status=status.HTTP_200_OK)
