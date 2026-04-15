from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any

import jwt

from .models import BlacklistedToken
from config import settings


class AuthService(ABC):
    """Интерфейс, который описывает, что должен делать сервис аутентификации"""

    @abstractmethod
    def extract_credentials(self, request: Any) -> Optional[str]:
        """Извлекает учетные данные из запроса"""
        pass

    @abstractmethod
    def create_session(self, user: Any) -> Dict[str, str]:
        """Создает сессию с пользователем"""
        pass

    @abstractmethod
    def validate_session(self, token: str) -> Optional[int]:
        """Проверяет данные аутентификации"""
        pass

    @abstractmethod
    def refresh_session(self, refresh_token: str) -> Dict[str, str]:
        """Обновляет сессию"""
        pass

    @abstractmethod
    def revoke_session(self, token: str) -> bool:
        """Заканчивает сессию"""
        pass


class JWTAuthService(AuthService):
    """Реализация аутентификации через JWT"""
    keyword = 'Bearer'

    def extract_credentials(self, request: Any) -> Optional[str]:
        """Извлекает access-токен из заголовка"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def create_session(self, user: Any) -> Dict[str, str]:
        """Возвращает словарь с access-токеном"""
        payload = {
            'user_id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return {"access": token}

    def validate_session(self, token: str) -> Optional[int]:
        """Проверяет access-токен и возвращает user_id"""
        # Если токен в черном списке, значит user разлогинился
        if BlacklistedToken.objects.filter(token=token).exists():
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload.get('user_id')
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return None

    def refresh_session(self, refresh_token: str) -> Dict[str, str]:
        """Обменивает refresh-токен на новую пару access/refresh"""
        # Пока не реализовано, выбрасываем исключение
        raise NotImplementedError("Refresh-схема будет доступна в версии 2.0")

    def revoke_session(self, token: str) -> bool:
        """Заносит access-токен в черный список"""
        try:
            # Декодируем токен без проверки подписи и срока годности,
            payload = jwt.decode(token, options={"verify_signature": False})

            # Извлекаем timestamp и переводим в datetime
            exp_timestamp = payload.get('exp')
            expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

            # Сохраняем в базу
            BlacklistedToken.objects.get_or_create(
                token=token,
                defaults={'expires_at': expires_at}
            )
            return True
        except (jwt.DecodeError, ValueError, TypeError):
            return False


auth_service = JWTAuthService()
