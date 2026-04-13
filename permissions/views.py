from rest_framework.viewsets import ModelViewSet

from .models import AccessRule, Role, BusinessElement
from .permissions import RBACPermission
from .serializers import AccessRuleSerializer, RoleSerializer, BusinessElementSerializer


class AccessRuleViewSet(ModelViewSet):
    """
    Все CRUD операции для правил доступа
    """
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer
    permission_classes = [RBACPermission]
    ordering = ['role', 'element']

class RoleViewSet(ModelViewSet):
    """
    Все CRUD операции для ролей
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [RBACPermission]

class BusinessElementViewSet(ModelViewSet):
    """
    Все CRUD операции для объектов приложения
    """
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [RBACPermission]