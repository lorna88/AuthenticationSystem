from rest_framework.permissions import BasePermission

from authentication.models import User
from .models import AccessRule, Role


class RBACPermission(BasePermission):
    """
    Система разграничения прав на основе ролей и владения объектом.
    """

    @staticmethod
    def get_action_name(method_name: str) -> str:
        """Маппинг HTTP-методов на ваши поля в БД"""
        mapping = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        return mapping.get(method_name)

    def has_permission(self, request, view):
        """
        Проверка прав на уровне эндпоинта.
        """
        user = request.user
        if not user:
            return False

        # Определяем, к какому элементу идет обращение
        element_slug = getattr(view, 'element_slug', None)
        if not element_slug:
            return False

        # Получаем название действия с элементом
        action = self.get_action_name(request.method)

        # Ищем правила для всех ролей пользователя
        if user.is_authenticated:
            # Юзер найден - получаем из базы
            user_roles = user.roles.all()
        else:
            # Иначе берем гостевые роли
            user_roles = Role.objects.filter(is_guest=True)

        rules = AccessRule.objects.filter(role__in=user_roles, element__slug=element_slug)

        # Проверяем наличие хотя бы одного обычного правила
        if user.is_authenticated and rules.filter(**{f"{action}_permission": True}).exists():
            return True

        # Проверяем наличие хотя бы одного правила с префиксом _all
        if rules.filter(**{f"{action}_all_permission": True}).exists():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Проверка прав на уровне конкретного объекта (владение).
        """
        user = request.user

        # Определяем, к какому элементу идет обращение
        element_slug = getattr(view, 'element_slug', None)

        # Получаем название действия с элементом
        action = self.get_action_name(request.method)

        # Ищем правила для всех ролей пользователя
        if user.is_authenticated:
            # Юзер найден - получаем из базы
            user_roles = user.roles.all()
        else:
            # Иначе берем гостевые роли
            user_roles = Role.objects.filter(is_guest=True)

        rules = AccessRule.objects.filter(role__in=user_roles, element__slug=element_slug)

        # Если есть право "All" — разрешаем доступ к любому объекту
        if rules.filter(**{f"{action}_all_permission": True}).exists():
            return True

        # Если есть обычное право — проверяем владельца
        if user.is_authenticated and rules.filter(**{f"{action}_permission": True}).exists():
            # Проверяем, совпадает ли ID пользователя с полем owner у объекта
            if isinstance(obj, User):
                return getattr(obj, 'id', None) == user.id
            return getattr(obj, 'owner_id', None) == user.id

        return False
