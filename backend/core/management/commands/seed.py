from django.core.management.base import BaseCommand
from customers.models import Customer
from products.models import Product
from orders.models import Order, OrderItem

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # Create sample customers
        customer1, created = Customer.objects.get_or_create(
            name="John Doe",
            email="john@example.com",
            phone="1234567890"
        )
        customer2, created = Customer.objects.get_or_create(
            name="Jane Smith",
            email="jane@example.com",
            phone="0987654321"
        )

        # Create sample products
        product1, created = Product.objects.get_or_create(
            name="Business Cards",
            description="High quality business cards.",
            category="Stationery",
            price=29.99,
            stock_quantity=100
        )
        product2, created = Product.objects.get_or_create(
            name="Flyers",
            description="Standard promotional flyers.",
            category="Print",
            price=19.99,
            stock_quantity=200
        )

        # Create sample orders and order items
        order1, created = Order.objects.get_or_create(
            customer=customer1,
            status="pending"
        )
        OrderItem.objects.get_or_create(
            order=order1,
            product=product1,
            quantity=2,
            price=29.99
        )

        order2, created = Order.objects.get_or_create(
            customer=customer2,
            status="processing"
        )
        OrderItem.objects.get_or_create(
            order=order2,
            product=product2,
            quantity=5,
            price=19.99
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully"))

