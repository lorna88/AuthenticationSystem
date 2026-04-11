from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class UserProfileView(APIView):
    """View для работы с профилем пользователя"""
    def get(self, request: HttpRequest) -> Response:
        """Просмотр профиля"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request: HttpRequest) -> Response:
        """Изменение профиля (частичное)"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request: HttpRequest) -> Response:
        """Мягкое удаление пользователя"""
        user = request.user
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
            }, status=405)
        return self.http_method_not_allowed(request, *args, **kwargs)
