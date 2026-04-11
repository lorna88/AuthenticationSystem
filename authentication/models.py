from django.db import models

from permissions.models import Role
from .crypt import make_password, check_password


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField(Role, related_name='users')

    def set_password(self, raw_password):
        """Хеширование пароля перед сохранением"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Проверка пароля при логине"""
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        """Для совместимости с DRF"""
        return True

    def __str__(self):
        return self.email
