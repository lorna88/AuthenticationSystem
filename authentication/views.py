from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.models import AccessRule
from permissions.permissions import RBACPermission, IsNotSystemUser, IsNotSystemObject
from .auth import auth_service
from .models import User
from .serializers import UserSerializer, RegisterSerializer, UserAdminSerializer


class LoginView(APIView):
    """View для аутентификации пользователя в системе"""
    permission_classes = []

    def post(self, request: Request) -> Response:
        """Проверяем email и пароль, и если они валидны, создаем сессию"""
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            return Response({"error": "Неверные данные"},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Аккаунт деактивирован"},
                            status=status.HTTP_401_UNAUTHORIZED)

        token = auth_service.create_session(user)
        return Response(token)


class LogoutView(APIView):
    """View для выхода пользователя из системы"""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Достаем учетные данные и завершаем сессию"""
        token = auth_service.extract_credentials(request)

        if not token:
            return Response(
                {"detail": "Токен не предоставлен или имеет неверный формат"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if auth_service.revoke_session(token):
            return Response({"detail": "Вы успешно вышли из системы"})
        return Response(
            {"detail": "Не удалось выполнить выход: невалидный токен"},
            status=status.HTTP_400_BAD_REQUEST
        )



class RegisterUserView(CreateAPIView):
    """View для регистрации пользователя."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = ()
    # authentication_classes = ()


class UserProfileView(APIView):
    """View для работы пользователя со своим профилем"""
    permission_classes = [IsAuthenticated, IsNotSystemUser]

    def get(self, request: Request) -> Response:
        """Просмотр профиля"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        """Изменение профиля (частичное)"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request) -> Response:
        """Мягкое удаление пользователя"""
        user = request.user
        user.is_active = False
        user.save()

        # Завершаем сессию с пользователем
        token = auth_service.extract_credentials(request)
        auth_service.revoke_session(token)

        return Response({"detail": "Аккаунт успешно деактивирован"}, status=204)

    def http_method_not_allowed(self, request: Request, *args, **kwargs) -> Response:
        """Убираем поддержку метода PUT в целях безопасности"""
        if request.method == "PUT":
            return Response({
                "error": f"Метод {request.method} не поддерживается.",
                "suggestion": "Пожалуйста, используйте PATCH для частичного обновления данных."
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return self.http_method_not_allowed(request, *args, **kwargs)


class UserManagementView(APIView):
    """View для управления всеми пользователями"""
    permission_classes = [RBACPermission, IsNotSystemObject]
    element_slug = 'users'

    def get(self, request: Request, pk: int=None) -> Response:
        """Просмотр списка пользователей либо профиля конкретного пользователя"""
        if pk:
            user = get_object_or_404(User, pk=pk)
            self.check_object_permissions(request, user)
            return Response(UserAdminSerializer(user).data)

        queryset = User.objects.filter(id=request.user.id)
        serializer = UserAdminSerializer(queryset, many=True)
        return Response(serializer.data)

    def patch(self, request: Request, pk: int) -> Response:
        """Частичное обновление данных пользователя"""
        # Находим пользователя по ID
        target_user = get_object_or_404(User, pk=pk)

        # Проверяем права: есть ли 'update_all'
        self.check_object_permissions(request, target_user)

        # Обновляем данные
        serializer = UserAdminSerializer(target_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int) -> Response:
        """Мягкое удаление пользователя"""
        # Находим пользователя
        target_user = get_object_or_404(User, pk=pk)

        # Проверяем права на 'delete_all'
        self.check_object_permissions(request, target_user)

        # Мягкое удаление (деактивация)
        target_user.is_active = False
        target_user.save()

        # Завершаем сессию с пользователем
        token = auth_service.extract_credentials(request)
        auth_service.revoke_session(token)

        return Response(
            {"detail": f"Пользователь {target_user.email} деактивирован"},
            status=status.HTTP_204_NO_CONTENT
        )

    def http_method_not_allowed(self, request: Request, *args, **kwargs) -> Response:
        """Методы POST и PUT не поддерживаются"""
        suggestion = ""
        if request.method == "POST":
            suggestion = "Для создания пользователя используйте эндпоинт регистрации /authentication/register/"
        if request.method == "PUT":
            suggestion = "Пожалуйста, используйте PATCH для частичного обновления данных."
        return Response({
            "error": f"Метод {request.method} не поддерживается.",
            "suggestion": suggestion
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

