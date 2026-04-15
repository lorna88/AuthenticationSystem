from typing import Any

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from .auth import auth_service
from .models import User


class CustomAuthentication(BaseAuthentication):
    """Реализация кастомной DRF аутентификации"""
    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        # Используем метод сервиса для извлечения учетных данных
        credential = auth_service.extract_credentials(request)

        if not credential:
            # Пропускаем, пользователь будет Anonymous
            return None

        # Используем метод получения активного пользователя
        user_id = auth_service.validate_session(credential)

        if user_id:
            user = User.objects.filter(id=user_id, is_active=True).first()
            if user:
                # Успех, DRF запишет его в request.user
                return (user, None)

        # Если учетные данные невалидны или юзер удален — ошибка 401
        raise exceptions.AuthenticationFailed('Пользователь не найден')

    def authenticate_header(self, request: Request) -> str | None:
        """Сообщаем DRF, какую аутентификацию используем"""
        return auth_service.keyword
