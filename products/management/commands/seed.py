"""Management command: seed sample catalogue data."""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from categories.models import Category
from products.models import Brand, Product, ProductImage
from accounts.models import User


class Command(BaseCommand):
    """Create a small sample catalogue for local development."""

    help = 'Seed sample categories, brands and products.'

    def handle(self, *args, **options):
        electronics = Category.objects.get_or_create(
            name='Electronics', defaults={'description': 'Gadgets and devices'}
        )[0]
        books = Category.objects.get_or_create(
            name='Books', defaults={'description': 'Print and digital books'}
        )[0]
        apparel = Category.objects.get_or_create(
            name='Apparel', defaults={'description': 'Clothing and accessories'}
        )[0]

        brand = Brand.objects.get_or_create(
            name='Acme', defaults={'description': 'Quality everyday tech'}
        )[0]

        samples = [
            ('Wireless Headphones', electronics, 79.99, 99.99, 25),
            ('Smart Watch', electronics, 149.99, 179.99, 15),
            ('Django for Professionals', books, 39.99, None, 100),
            ('Cotton T-Shirt', apparel, 19.99, 24.99, 200),
            ('Mechanical Keyboard', electronics, 89.99, None, 40),
        ]

        created = 0
        for name, category, price, compare, stock in samples:
            if Product.objects.filter(sku=slugify(name)[:20]).exists():
                continue
            Product.objects.create(
                name=name,
                sku=slugify(name)[:20],
                category=category,
                brand=brand,
                price=price,
                compare_at_price=compare,
                stock=stock,
                is_new=True,
                featured=True,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created} products across {Category.objects.count()} categories.'
        ))
