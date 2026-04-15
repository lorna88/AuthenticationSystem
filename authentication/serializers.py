from typing import Any

from rest_framework import serializers

from permissions.models import Role
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Проверка совпадения паролей
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data: dict[str, Any]) -> User:
        """
        Создание пользователя с хешированием пароля
        """
        # Удаляем лишнее поле, которого нет в модели
        validated_data.pop('password_confirm')

        # Создаем объект пользователя, но не сохраняем сразу
        user = User(
            email=validated_data['email'],
            full_name=validated_data['full_name']
        )

        # Хешируем пароль
        user.set_password(validated_data['password'])

        # Сохраняем в БД
        user.save()

        # Добавляем роли по умолчанию
        default_roles = Role.objects.filter(is_default_role=True)
        if default_roles.exists():
            user.roles.add(*default_roles)

        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра, обновления и удаления профиля"""
    class Meta:
        model = User
        fields = ['email', 'full_name']
        read_only_fields = ['email']

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Логика обновления профиля"""
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.save()
        return instance


class UserAdminSerializer(UserSerializer):
    """Сериализатор для эндпоинта /users/ (админка)"""
    roles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all()
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['id', 'is_active', 'roles', 'created_at']
        read_only_fields = ['id', 'email', 'created_at']

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Логика обновления профиля для админа"""
        instance.is_active = validated_data.get('is_active', instance.is_active)

        # Обновляем все роли пользователя
        if 'roles' in validated_data:
            roles = validated_data.pop('roles')
            instance.roles.set(roles)

        return super().update(instance, validated_data)
