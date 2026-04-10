from typing import Any

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Role, BusinessElement, AccessRule


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ролей"""
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug']

    def validate_slug(self, value):
        """Приводим слаг к нижнему регистру для консистентности"""
        return value.lower()


class BusinessElementSerializer(serializers.ModelSerializer):
    """Сериализатор для модели бизнес-элементов"""
    class Meta:
        model = BusinessElement
        fields = ['id', 'name', 'slug']

    def validate_slug(self, value):
        """Приводим слаг к нижнему регистру для консистентности"""
        return value.lower()


class AccessRuleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели настройки прав доступа"""
    role_name = serializers.ReadOnlyField(source='role.name')
    element_name = serializers.ReadOnlyField(source='element.name')

    class Meta:
        model = AccessRule
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=AccessRule.objects.all(),
                fields=['role', 'element'],
                message="Для этой роли уже настроены правила доступа к данному элементу."
            )
        ]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Логическая валидация: если разрешено 'all',
        то логично, что обычное разрешение тоже должно быть True.
        """

        permission_pairs = [
            ('read_all_permission', 'read_permission'),
            ('update_all_permission', 'update_permission'),
            ('delete_all_permission', 'delete_permission'),
        ]

        for all_perm, single_perm in permission_pairs:
            if data.get(all_perm) and not data.get(single_perm):
                data[single_perm] = True
        return data