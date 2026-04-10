from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AccessRuleViewSet, RoleViewSet, BusinessElementViewSet

app_name = 'permissions'

router = DefaultRouter()
router.register(r'access_rules', AccessRuleViewSet, basename='access_rule')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'elements', BusinessElementViewSet, basename='element')

urlpatterns = [
    path('', include(router.urls)),
]