from django.db import models

class Role(models.Model):
    """Model for roles"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Model for business elements"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class AccessRule(models.Model):
    """Model for access roles rules"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='rules')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='rules')
    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.role.name} {self.element.name}'
