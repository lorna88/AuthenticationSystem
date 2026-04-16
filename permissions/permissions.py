from rest_framework.permissions import BasePermission

from .models import AccessRule, Role, BusinessElement


class RBACPermission(BasePermission):
    """
    Система разграничения прав на основе ролей и владения объектом.
    """

    @staticmethod
    def get_action_name(method_name: str) -> str:
        """Маппинг HTTP-методов на поля в БД"""
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

        # Системный пользователь имеет доступ ко всем элементам
        if getattr(user, 'is_system', False):
            return True

        # Определяем, к какому элементу идет обращение
        element_slug = getattr(view, 'element_slug', None)
        if not element_slug:
            return False

        # Получаем название действия с элементом
        action = self.get_action_name(request.method)
        if not action:
            return False

        # Ищем правила для всех ролей пользователя
        if user.is_authenticated:
            # Юзер найден - получаем из базы
            user_roles = user.roles.all()
        else:
            # Иначе берем гостевые роли
            user_roles = Role.objects.filter(is_guest=True)

        if not user_roles.exists():
            return False

        rules = AccessRule.objects.filter(role__in=user_roles, element__slug=element_slug)

        element_is_system = BusinessElement.objects.filter(
            slug=element_slug,
            is_system=True
        ).exists()

        # Определяем права доступа для системных таблиц
        if element_is_system:
            if action == 'create':
                return rules.filter(**{"create_permission": True}).exists()
            return rules.filter(**{f"{action}_all_permission": True}).exists()

        # Проверяем наличие хотя бы одного правила с префиксом _all
        if action != 'create' and rules.filter(**{f"{action}_all_permission": True}).exists():
            return True

        # Проверяем наличие хотя бы одного обычного правила
        if user.is_authenticated and rules.filter(**{f"{action}_permission": True}).exists():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Проверка прав на уровне конкретного объекта (владение).
        """
        user = request.user

        # Системный пользователь имеет доступ ко всем элементам
        if getattr(user, 'is_system', False):
            return True

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

        element_is_system = BusinessElement.objects.filter(
            slug=element_slug,
            is_system=True
        ).exists()

        # Определяем права доступа для системных таблиц
        if element_is_system:
            return rules.filter(**{f"{action}_all_permission": True}).exists()

        # Если есть право "All" — разрешаем доступ к любому объекту
        if rules.filter(**{f"{action}_all_permission": True}).exists():
            return True

        # Если есть обычное право — проверяем владельца
        if user.is_authenticated and rules.filter(**{f"{action}_permission": True}).exists():
            # Проверяем, совпадает ли ID пользователя с полем owner у объекта
            if isinstance(obj, dict):
                owner_id = obj.get('owner_id', None)
            else:
                owner_id = getattr(obj, 'owner_id', None)
            return owner_id == user.id

        return False


class IsNotSystemUser(BasePermission):
    """
    Доступ для не системного пользователя.
    """
    def has_permission(self, request, view):
        """
        Проверяем атрибут is_system.
        """
        return request.user and not getattr(request.user, 'is_system', False)


class IsNotSystemObject(BasePermission):
    """
    Запрещает доступ к объектам, у которых is_system=True.
    """
    def has_object_permission(self, request, view, obj):
        # Проверяем, не является ли объект системным
        return not getattr(obj, 'is_system', False)
