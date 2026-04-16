from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from business_mock.services import get_object, get_filtered_list
from permissions.permissions import RBACPermission


class ProductMockView(APIView):
    """
    Mock-View для демонстрации системы прав.
    Ресурс: 'products'
    """
    permission_classes = [RBACPermission]
    element_slug = 'products'

    def get_mock_data(self):
        """Эмуляция данных в БД (в реальном проекте это была бы модель Product)"""
        return [
            {
                "id": 1,
                "name": "Ноутбук Pro Max 16",
                "price": 150000,
                "category": "Электроника",
                "shop_id": 10,
                "owner_id": 2
            },
            {
                "id": 2,
                "name": "Кофемашина Espresso Express",
                "price": 45000,
                "category": "Техника для кухни",
                "shop_id": 11,
                "owner_id": 2
            },
            {
                "id": 3,
                "name": "Беспроводные наушники AirSound",
                "price": 12000,
                "category": "Аксессуары",
                "shop_id": 10,
                "owner_id": 2
            },
            {
                "id": 4,
                "name": "Смарт-часы FitTrack",
                "price": 8000,
                "category": "Электроника",
                "shop_id": 12,
                "owner_id": 2
            }
        ]

    def get(self, request: Request, pk: int = None) -> Response:
        """Просмотр списка продуктов либо деталей конкретного продукта"""
        if pk:
            product = get_object(pk, self.get_mock_data)
            if not product:
                return Response({"detail": "Товар не найден"},
                                status=status.HTTP_404_NOT_FOUND)

            self.check_object_permissions(request, product)
            return Response(product)

        # Для списка делаем фильтрацию
        products = get_filtered_list(request.user, self.element_slug, self.get_mock_data)
        return Response(products)

    def post(self, request: Request) -> Response:
        """Создание нового товара"""
        return Response({
            "detail": "Товар успешно создан",
            "data": request.data,
            "owner_id": request.user.id
        }, status=status.HTTP_201_CREATED)

    def patch(self, request: Request, pk: int) -> Response:
        """Редактирование товара"""
        product = get_object(pk, self.get_mock_data)
        if not product:
            return Response({"detail": "Товар не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        # Проверка прав на редактирование
        self.check_object_permissions(request, product)

        return Response({"detail": f"Товар {pk} обновлен", "new_data": request.data})

    def delete(self, request: Request, pk: int) -> Response:
        """Удаление товара"""
        product = get_object(pk, self.get_mock_data)
        if not product:
            return Response({"detail": "Товар не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        # Проверка прав на удаление
        self.check_object_permissions(request, product)

        return Response({"detail": f"Товар {pk} удален"},
                        status=status.HTTP_204_NO_CONTENT)
