from typing import Callable, Any

from permissions.models import Role, AccessRule


def get_object(pk, get_data: Callable) -> Any:
    """Получение объекта по pk"""
    all_objects = get_data()
    return next((item for item in all_objects if item["id"] == pk), None)


def get_filtered_list(user: Any, element_slug: str, get_data: Callable) -> list[Any]:
    """Фильтрация списка объектов согласно установленным правам"""
    # Получаем правила для текущего пользователя через его роли
    if user.is_authenticated:
        user_roles = user.roles.all()
    else:
        user_roles = Role.objects.filter(is_guest=True)
    rules = AccessRule.objects.filter(role__in=user_roles, element__slug=element_slug)

    all_objects = get_data()
    # Логика фильтрации:
    if rules.filter(read_all_permission=True).exists():
        # Если есть право "читать всё" — отдаем весь список
        return all_objects

    if rules.filter(read_permission=True).exists():
        # Если только "свои" — фильтруем по owner_id
        filtered_objects = [o for o in all_objects if o["owner_id"] == user.id]
        return filtered_objects

    return []