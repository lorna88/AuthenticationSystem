from rest_framework import serializers

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
        fields = [
            'id', 'role', 'role_name', 'element', 'element_name',
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission'
        ]

    @staticmethod
    def validate_boolean(name, value: str) -> None:
        """
        Проверка валидности булевского значения
        """
        if value.lower() != 'true' and value.lower() != 'false':
            raise serializers.ValidationError({name: 'Значение должно быть true или false.'})

    def validate_role(self, value: int) -> int:
        """
        Проверка существования роли
        """
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError({'role': 'Роль с таким ID отсутствует в системе.'})
        return value

    def validate_element(self, value: int) -> int:
        """
        Проверка существования бизнес-элемента
        """
        if not BusinessElement.objects.filter(id=value).exists():
            raise serializers.ValidationError({'element': 'Элемент с таким ID отсутствует в системе.'})
        return value

    def validate_read_permission(self, value: str) -> str:
        self.validate_boolean(value, 'read_permission')
        return value

    def validate_read_all_permission(self, value: str) -> str:
        self.validate_boolean(value, 'read_all_permission')
        return value

    def validate_create_permission(self, value: str) -> str:
        self.validate_boolean(value, 'create_permission')
        return value

    def validate_update_permission(self, value: str) -> str:
        self.validate_boolean(value, 'update_permission')
        return value

    def validate_update_all_permission(self, value: str) -> str:
        self.validate_boolean(value, 'update_all_permission')
        return value

    def validate_delete_permission(self, value: str) -> str:
        self.validate_boolean(value, 'delete_permission')
        return value

    def validate_delete_all_permission(self, value: str) -> str:
        self.validate_boolean(value, 'delete_all_permission')
        return value

    def validate(self, data):
        """
        Логическая валидация: если разрешено 'all',
        то логично, что обычное разрешение тоже должно быть True.
        """
        if data.get('read_all_permission') and not data.get('read_permission'):
            data['read_permission'] = True
        if data.get('update_all_permission') and not data.get('update_permission'):
            data['update_permission'] = True
        if data.get('delete_all_permission') and not data.get('delete_permission'):
            data['delete_permission'] = True
        return data