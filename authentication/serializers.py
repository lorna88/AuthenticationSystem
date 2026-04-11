from typing import Any

from rest_framework import serializers

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
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра, обновления и удаления профиля"""
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'created_at']
        read_only_fields = ['id', 'email', 'created_at']

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Логика обновления профиля"""
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.save()
        return instance