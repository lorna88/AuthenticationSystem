from django.db import models

class Role(models.Model):
    """Модель для ролей"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_guest = models.BooleanField(default=False)
    is_default_role = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Модель для бизнес-элементов"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_system = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AccessRule(models.Model):
    """Модель для прав доступа по ролям и видам ресурсов"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='rules')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='rules')
    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        # У одной роли может быть только одно правило для конкретного элемента
        unique_together = ('role', 'element')
        verbose_name = "Правило доступа"
        verbose_name_plural = "Правила доступа"

    def __str__(self):
        return f'{self.role.name} {self.element.name}'
