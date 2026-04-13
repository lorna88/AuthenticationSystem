from typing import Callable

from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from .auth import auth_service
from .models import User


class AuthMiddleware:
    """
    Кастомный middleware для проверки учетных данных пользователя
    при отправке запроса к ресурсу.
    Если пользователь прислал данные авторизации и он найден в базе,
    передаем его в request.
    Если пользователь, прислав запрос, не авторизуется, считаем его
    гостем.
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: Request) -> Response:
        # Просим сервис достать токен
        credential = auth_service.extract_credentials(request)

        if not credential:
            request.user = AnonymousUser()
            return self.get_response(request)

        # Просим сервис валидировать верификационные данные
        user_id = auth_service.validate_session(credential)
        if user_id:
            user = User.objects.filter(id=user_id, is_active=True).first()
            if user:
                request.user = user
                return self.get_response(request)

        # Если данные были, но юзер не найден/неактивен — возвращаем ошибку 401
        return Response({"detail": "Пользователь не найден"},
                        status=status.HTTP_401_UNAUTHORIZED)