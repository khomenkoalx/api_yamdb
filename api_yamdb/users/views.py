from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from users.serializers import SignUpSerializer, UserMeProfileSerializer, TokenSerializer, UserSerializer
from rest_framework_simplejwt.tokens import AccessToken
from api.permissions import IsAdmin
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.username != username:
                return Response(
                    {"email": "Пользователь с таким email уже существует."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if existing_user.email != email:
                return Response(
                    {"username": "Пользователь с таким username уже существует."},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            return Response({"detail": "Неверный код подтверждения"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = AccessToken.for_user(user)
        return Response({
            'access': str(access_token),
        }, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = [SearchFilter]
    search_fields = ['username']
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return [IsAdmin()]

    @action(detail=False, methods=['get', 'patch', 'delete'], url_path='me')
    def me(self, request):
        if request.method == 'DELETE':
            return Response(
                {"detail": "Метод 'DELETE' не разрешён."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        user = request.user

        if request.method == 'GET':
            serializer = UserMeProfileSerializer(user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = UserMeProfileSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
