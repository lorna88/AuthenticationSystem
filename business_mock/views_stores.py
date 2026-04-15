from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from business_mock.services import get_object, get_filtered_list
from permissions.permissions import RBACPermission


class StoreMockView(APIView):
    """
    Mock-View для демонстрации системы прав.
    Ресурс: 'stores'
    """
    permission_classes = [RBACPermission]
    element_slug = 'stores'

    def get_mock_data(self):
        """Эмуляция данных в БД (в реальном проекте это была бы модель Store)"""
        return [
            {
                "id": 1,
                "name": "Гипермаркет 'Центральный'",
                "address": "ул. Ленина, д. 1",
                "city": "Москва",
                "owner_id": 2
            },
            {
                "id": 2,
                "name": "Магазин электроники 'ТехноМир'",
                "address": "пр. Мира, д. 45",
                "city": "Санкт-Петербург",
                "owner_id": 2
            },
            {
                "id": 3,
                "name": "Бутик 'Стиль и Уют'",
                "address": "ул. Садовая, д. 12",
                "city": "Казань",
                "owner_id": 2
            }
        ]

    def get(self, request: Request, pk: int=None) -> Response:
        """Просмотр списка магазинов либо деталей конкретного магазина"""
        if pk:
            store = get_object(pk, self.get_mock_data)
            if not store:
                return Response({"detail": "Магазин не найден"},
                                status=status.HTTP_404_NOT_FOUND)

            self.check_object_permissions(request, store)
            return Response(store)

        # Для списка делаем фильтрацию
        stores = get_filtered_list(request.user, self.element_slug, self.get_mock_data)
        return Response(stores)

    def post(self, request:Request) -> Response:
        """Создание нового магазина"""
        return Response({
            "detail": "Магазин успешно создан",
            "data": request.data,
            "owner_id": request.user.id
        }, status=status.HTTP_201_CREATED)

    def patch(self, request: Request, pk: int) -> Response:
        """Редактирование магазина"""
        store = get_object(pk, self.get_mock_data)
        if not store:
            return Response({"detail": "Магазин не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        # Проверка прав на редактирование
        self.check_object_permissions(request, store)

        return Response({"detail": f"Магазин {pk} обновлен", "new_data": request.data})

    def delete(self, request: Request, pk: int) -> Response:
        """Удаление магазина"""
        store = get_object(pk, self.get_mock_data)
        if not store:
            return Response({"detail": "Магазин не найден"},
                            status=status.HTTP_404_NOT_FOUND)

        # Проверка прав на удаление
        self.check_object_permissions(request, store)

        return Response({"detail": f"Магазин {pk} удален"},
                        status=status.HTTP_204_NO_CONTENT)
