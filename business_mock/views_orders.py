from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from business_mock.services import get_object, get_filtered_list
from permissions.permissions import RBACPermission


class OrderMockView(APIView):
    """
    Mock-View для демонстрации системы прав.
    Ресурс: 'orders'
    """
    permission_classes = [RBACPermission]
    element_slug = 'orders'

    def get_mock_data(self):
        """Эмуляция данных в БД (в реальном проекте это была бы модель Order)"""
        return [
            {"id": 1, "name": "Заказ Apple iPhone", "owner_id": 1},  # Владелец - Admin
            {"id": 2, "name": "Заказ Samsung TV", "owner_id": 2},  # Владелец - Manager
            {"id": 3, "name": "Заказ Кофемашина", "owner_id": 3},  # Владелец - User
            {"id": 4, "name": "Заказ Ноутбук", "owner_id": 2},  # Владелец - Manager
        ]

    def get(self, request: Request, pk: int=None) -> Response:
        """Просмотр списка заказов либо деталей конкретного заказа"""
        if pk:
            order = get_object(pk, self.get_mock_data)
            if not order:
                return Response({"detail": "Заказ не найден"},
                                status=status.HTTP_404_NOT_FOUND)

            self.check_object_permissions(request, order)
            return Response(order)

        # Для списка делаем фильтрацию
        orders = get_filtered_list(request.user, self.element_slug, self.get_mock_data)
        if not orders:
            self.permission_denied(request, message="У вас нет прав на просмотр заказов.")
        return Response(orders)

    def post(self, request:Request) -> Response:
        """Создание нового заказа"""
        return Response({
            "detail": "Заказ успешно создан",
            "data": request.data,
            "owner_id": request.user.id
        }, status=status.HTTP_201_CREATED)

    def patch(self, request: Request, pk: int) -> Response:
        """Редактирование заказа"""
        order = get_object(pk, self.get_mock_data)
        if not order:
            return Response({"detail": "Заказ не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        # Проверка прав на редактирование
        self.check_object_permissions(request, order)

        return Response({"detail": f"Заказ {pk} обновлен", "new_data": request.data})

    def delete(self, request: Request, pk: int) -> Response:
        """Удаление заказа"""
        order = get_object(pk, self.get_mock_data)
        if not order:
            return Response({"detail": "Заказ не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        # Проверка прав на удаление
        self.check_object_permissions(request, order)

        return Response({"detail": f"Заказ {pk} удален"},
                        status=status.HTTP_204_NO_CONTENT)
