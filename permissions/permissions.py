from rest_framework.permissions import BasePermission

from .models import AccessRule


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
        # Если пользователь не аутентифицирован (Middleware не сработал)
        if not request.user or not request.user.is_authenticated:
            return False

        # Определяем, к какому элементу идет обращение
        element_slug = getattr(view, 'element_slug', None)
        if not element_slug:
            return False

        # Получаем название действия с элементом
        action = self.get_action_name(request.method)

        # Ищем правила для всех ролей пользователя
        user_roles = request.user.roles.all()
        rules = AccessRule.objects.filter(role__in=user_roles, element__slug=element_slug)

        # Проверяем наличие хотя бы одного правила с префиксом _all либо без префикса
        return (rules.filter(**{f"{action}_permission": True}).exists() or
                rules.filter(**{f"{action}_all_permission": True}).exists())

    def has_object_permission(self, request, view, obj):
        """
        Проверка прав на уровне конкретного объекта (владение).
        """
        # Определяем, к какому элементу идет обращение
        element_slug = getattr(view, 'element_slug', None)

        # Получаем название действия с элементом
        action = self.get_action_name(request.method)

        # Ищем правила для всех ролей пользователя
        user_roles = request.user.roles.all()
        rules = AccessRule.objects.filter(role__in=user_roles, element__slug=element_slug)

        # Если есть право "All" — разрешаем доступ к любому объекту
        if rules.filter(**{f"{action}_all_permission": True}).exists():
            return True

        # Если есть обычное право — проверяем владельца
        if rules.filter(**{f"{action}_permission": True}).exists():
            # Проверяем, совпадает ли ID пользователя с полем owner у объекта
            return getattr(obj, 'owner_id', None) == request.user.id

        return False