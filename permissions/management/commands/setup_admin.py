import getpass

from django.core.management import BaseCommand
from django.db import transaction

from authentication.models import User
from permissions.models import Role, BusinessElement, AccessRule


class Command(BaseCommand):
    help = 'Первоначальная настройка системы: создание ролей, прав и суперпользователя'

    PERMISSIONS_MAP = {
        'admin': {
            'users': {'read_all_permission': True, 'update_all_permission': True,
                      'delete_all_permission': True},
            'roles': {'read_all_permission': True, 'update_all_permission': True,
                      'create_permission': True, 'delete_all_permission': True},
            'business_elements': {'read_all_permission': True, 'update_all_permission': True,
                                  'create_permission': True, 'delete_all_permission': True},
            'access_rules': {'read_all_permission': True, 'update_all_permission': True,
                             'create_permission': True, 'delete_all_permission': True},
        },

        'manager': {
            'users': {'read_all_permission': True},
            'orders': {'read_all_permission': True},
            'products': {'create_permission': True, 'update_all_permission': True,
                         'delete_all_permission': True},
            'stores': {'create_permission': True, 'update_all_permission': True,
                       'delete_all_permission': True},
        },

        'user': {
            'orders': {'read_permission': True, 'create_permission': True,
                       'update_permission': True, 'delete_permission': True},
            'products': {'read_all_permission': True},
            'stores': {'read_all_permission': True},
        },

        'guest': {
            'products': {'read_all_permission': True},
            'stores': {'read_all_permission': True},
        }
    }

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Запуск начальной настройки системы ---'))

        try:
            # Создание системных ролей
            admin_role, _ = Role.objects.get_or_create(
                slug='admin',
                defaults={'name': 'Администратор', 'is_guest': False, 'is_default_role': False}
            )
            manager_role, _ = Role.objects.get_or_create(
                slug='manager',
                defaults={'name': 'Менеджер', 'is_guest': False, 'is_default_role': False}
            )
            user_role, _ = Role.objects.get_or_create(
                slug='user',
                defaults={'name': 'Пользователь', 'is_guest': False, 'is_default_role': True}
            )
            guest_role, _ = Role.objects.get_or_create(
                slug='guest',
                defaults={'name': 'Гость', 'is_guest': True, 'is_default_role': False}
            )

            # Создание элементов ресурсов
            elements_data = [
                # Системные элементы
                ('Пользователи', 'users', True),
                ('Роли', 'roles', True),
                ('Правила доступа', 'access_rules', True),
                ('Бизнес-элементы', 'business_elements', True),

                # Тестовые бизнес-объекты
                ('Товары', 'products', False),
                ('Магазины', 'stores', False),
                ('Заказы', 'orders', False),
            ]

            elements = []
            for name, slug, is_system in elements_data:
                el, _ = BusinessElement.objects.get_or_create(
                    slug=slug,
                    defaults={'name': name, 'is_system': is_system}
                )
                elements.append(el)

            # Настройка прав доступа
            for role_slug, elements in self.PERMISSIONS_MAP.items():
                # Находим роль
                role = Role.objects.get(slug=role_slug)

                for element_slug, perms in elements.items():
                    # Находим элемент
                    element = BusinessElement.objects.get(slug=element_slug)

                    # Обновляем или создаем правила
                    AccessRule.objects.update_or_create(
                        role=role,
                        element=element,
                        defaults=perms
                    )
                    self.stdout.write(f"Настроены права: {role_slug} -> {element_slug}")

            self.stdout.write(self.style.SUCCESS('Базовая структура прав создана.'))

            # Создание суперпользователя
            self.stdout.write('\nСоздание учетной записи суперпользователя:')
            email = input('Email: ')
            full_name = input('Полное имя: ')
            password = getpass.getpass('Пароль: ')

            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.ERROR(f'Пользователь с email {email} уже существует.'))
                return

            user = User(email=email, full_name=full_name)
            user.set_password(password)
            user.is_system = True
            user.save()

            self.stdout.write(self.style.SUCCESS(f'\nСуперпользователь {email} успешно создан!'))
            self.stdout.write(self.style.WARNING('Теперь вы можете войти в систему через API.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка при настройке: {e}'))
