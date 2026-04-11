from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.models import AccessRule
from permissions.permissions import RBACPermission
from .models import User
from .serializers import UserSerializer, RegisterSerializer


class RegisterUserView(CreateAPIView):
    """View для регистрации пользователя."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = ()
    # authentication_classes = ()


class UserProfileView(APIView):
    """View для работы пользователя со своим профилем"""

    def get(self, request: HttpRequest) -> Response:
        """Просмотр профиля"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request: HttpRequest) -> Response:
        """Изменение профиля (частичное)"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: HttpRequest) -> Response:
        """Мягкое удаление пользователя"""
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user.is_active = False
        user.save()

        # Инвалидируем токен (добавляем в Blacklist)
        return Response({"detail": "Аккаунт успешно деактивирован"}, status=204)

    def http_method_not_allowed(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Убираем поддержку метода PUT в целях безопасности"""
        if request.method == "PUT":
            return Response({
                "error": f"Метод {request.method} не поддерживается.",
                "suggestion": "Пожалуйста, используйте PATCH для частичного обновления данных."
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return self.http_method_not_allowed(request, *args, **kwargs)


class UserManagementView(APIView):
    """View для управления всеми пользователями"""
    permission_classes = [RBACPermission]
    element_slug = 'users'

    def get_filtered_users(self, request: HttpRequest) -> Response:
        """Фильтрация пользователей согласно имеющимся правам"""
        user = request.user

        # Получаем все правила для текущего пользователя по этому ресурсу
        rules = AccessRule.objects.filter(
            role__in=user.roles.all(),
            element__slug=self.element_slug
        )

        # Если хотя бы одна роль дает право "Видеть всех"
        if rules.filter(read_all_permission=True).exists():
            queryset = User.objects.all()
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data)

        # Если есть только право "Видеть себя" (read_permission)
        if rules.filter(read_permission=True).exists():
            # В данном случае "свой" объект для пользователя — это он сам
            queryset = User.objects.filter(id=user.id)
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data)

        # Если нет ни одного из прав — возвращаем ошибку 403.
        return Response({"detail": "У вас нет прав на просмотр пользователей"},
                        status=status.HTTP_403_FORBIDDEN)

    def get(self, request: HttpRequest, pk: int=None) -> Response:
        """Просмотр списка пользователей либо профиля конкретного пользователя"""
        if pk:
            # Если есть read_all_permission — увидит любого.
            # Если только read_permission — увидит только если pk == request.user.id
            user = get_object_or_404(User, pk=pk)
            self.check_object_permissions(request, user)
            return Response(UserSerializer(user).data)

        # Логика фильтрации списка
        return self.get_filtered_users(request)

    def patch(self, request: HttpRequest, pk: int) -> Response:
        """Частичное обновление данных пользователя"""
        # Находим пользователя по ID
        target_user = get_object_or_404(User, pk=pk)

        # Проверяем права: есть ли 'update_all' или ('update' и это сам пользователь)
        self.check_object_permissions(request, target_user)

        # Обновляем данные
        serializer = UserSerializer(target_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: HttpRequest, pk: int) -> Response:
        """Мягкое удаление пользователя"""
        # Находим пользователя
        target_user = get_object_or_404(User, pk=pk)

        # Проверяем права на 'delete_all' или ('delete' и это сам пользователь)
        self.check_object_permissions(request, target_user)

        # Мягкое удаление (деактивация)
        target_user.is_active = False
        target_user.save()

        return Response(
            {"detail": f"Пользователь {target_user.email} деактивирован"},
            status=status.HTTP_204_NO_CONTENT
        )

    def http_method_not_allowed(self, request: HttpRequest, *args, **kwargs) -> Response:
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

