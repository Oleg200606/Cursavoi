from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from shopapp.models import Product, Category, Tag

class Command(BaseCommand):
    help = 'Creates initial users and groups with permissions'

    def handle(self, *args, **options):
        # Создание групп
        superuser_group, _ = Group.objects.get_or_create(name='Superuser')
        seller_group, _ = Group.objects.get_or_create(name='Seller')
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        customer_group, _ = Group.objects.get_or_create(name='Customer')

        # Получение всех разрешений для моделей
        product_perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Product))
        category_perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Category))
        tag_perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Tag))

        # Назначение прав группам
        # Продавцам - права на товары (кроме физического удаления)
        seller_perms = [
            p for p in product_perms 
            if not p.codename.startswith('delete') and p.codename != 'view_product'
        ]
        seller_group.permissions.set(seller_perms)

        # Администраторам - все права на товары, категории и теги
        admin_perms = list(product_perms) + list(category_perms) + list(tag_perms)
        admin_group.permissions.set(admin_perms)

        # Покупателям - только просмотр
        customer_group.permissions.set([
            Permission.objects.get(codename='view_product'),
            Permission.objects.get(codename='view_category'),
            Permission.objects.get(codename='view_tag'),
        ])

        # Создание суперпользователя
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        superuser.groups.add(superuser_group)
        self.stdout.write(self.style.SUCCESS('Superuser created: admin (password: admin123)'))

        # Создание продавцов
        for i in range(1, 4):
            seller = User.objects.create_user(
                username=f'seller{i}',
                email=f'seller{i}@example.com',
                password=f'seller{i}123'
            )
            seller.groups.add(seller_group)
            self.stdout.write(self.style.SUCCESS(f'Seller {i} created: seller{i} (password: seller{i}123)'))

        # Создание администраторов
        for i in range(1, 3):
            admin = User.objects.create_user(
                username=f'admin{i}',
                email=f'admin{i}@example.com',
                password=f'admin{i}123',
                is_staff=True
            )
            admin.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'Admin {i} created: admin{i} (password: admin{i}123)'))

        # Создание покупателей
        for i in range(1, 5):
            customer = User.objects.create_user(
                username=f'customer{i}',
                email=f'customer{i}@example.com',
                password=f'customer{i}123'
            )
            customer.groups.add(customer_group)
            self.stdout.write(self.style.SUCCESS(f'Customer {i} created: customer{i} (password: customer{i}123)'))