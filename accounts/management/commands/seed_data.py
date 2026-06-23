from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile, RiderProfile
from products.models import Category, Product
from orders.models import Cart, Order, OrderItem, DeliveryAddress
from riders.models import RiderOrderAction
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with sample data for SwiftCart Logistics"

    def handle(self, *args, **options):
        self.stdout.write("Clearing database tables...")
        
        RiderOrderAction.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Cart.objects.all().delete()
        DeliveryAddress.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        RiderProfile.objects.all().delete()
        CustomerProfile.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("Database cleared. Starting seeding...")

        try:
            with transaction.atomic():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@swiftcart.com',
                    password='adminpassword123',
                    role=User.Role.ADMIN
                )
                self.stdout.write("Created Admin: admin / adminpassword123")

                cust1 = User.objects.create_user(
                    username='john_doe',
                    email='john@example.com',
                    password='customerpass123',
                    role=User.Role.CUSTOMER
                )
                CustomerProfile.objects.create(
                    user=cust1,
                    phone_number='+1555123456',
                    address='123 Main St, New York, NY 10001'
                )
                Cart.objects.create(customer=cust1)
                
                cust2 = User.objects.create_user(
                    username='jane_smith',
                    email='jane@example.com',
                    password='customerpass123',
                    role=User.Role.CUSTOMER
                )
                CustomerProfile.objects.create(
                    user=cust2,
                    phone_number='+1555987654',
                    address='456 Oak Ave, Los Angeles, CA 90001'
                )
                Cart.objects.create(customer=cust2)

                self.stdout.write("Created Customers: john_doe, jane_smith / customerpass123")

                rider1 = User.objects.create_user(
                    username='rider_mike',
                    email='mike@example.com',
                    password='riderpass123',
                    role=User.Role.RIDER
                )
                RiderProfile.objects.create(
                    user=rider1,
                    phone_number='+1555444555',
                    is_online=True
                )

                rider2 = User.objects.create_user(
                    username='rider_sarah',
                    email='sarah@example.com',
                    password='riderpass123',
                    role=User.Role.RIDER
                )
                RiderProfile.objects.create(
                    user=rider2,
                    phone_number='+1555777888',
                    is_online=False
                )

                self.stdout.write("Created Riders: rider_mike (Online), rider_sarah (Offline) / riderpass123")

                cat_elec = Category.objects.create(name='Electronics', description='Gadgets, devices, and warehouse electronic systems.')
                cat_gro = Category.objects.create(name='Groceries', description='Fresh food, beverages, and household goods.')
                cat_wear = Category.objects.create(name='Warehouse Essentials', description='Boxes, packing tapes, bubble wraps, and protective gear.')

                self.stdout.write("Created Categories.")

                p1 = Product.objects.create(
                    category=cat_elec,
                    name='Smart Courier Scanner',
                    description='Rugged barcode and QR scanner for inventory tracking.',
                    price=249.99,
                    stock_quantity=15,
                    is_active=True
                )
                p2 = Product.objects.create(
                    category=cat_elec,
                    name='Portable Thermal Printer',
                    description='Bluetooth label printer for packages and receipts.',
                    price=89.50,
                    stock_quantity=3,
                    is_active=True
                )
                p3 = Product.objects.create(
                    category=cat_wear,
                    name='Heavy Duty Packing Tape (6 Pack)',
                    description='High adhesive packing tape rolls for secure shipping.',
                    price=18.99,
                    stock_quantity=50,
                    is_active=True
                )
                p4 = Product.objects.create(
                    category=cat_wear,
                    name='Cardboard Shipping Boxes (Medium, 25 Pack)',
                    description='Double-walled corrugated cardboard boxes.',
                    price=35.00,
                    stock_quantity=4,
                    is_active=True
                )
                p5 = Product.objects.create(
                    category=cat_gro,
                    name='Energy Drink Pack (24 Cans)',
                    description='Assorted caffeine energy drinks for warehouse staff and riders.',
                    price=42.00,
                    stock_quantity=10,
                    is_active=True
                )

                self.stdout.write("Created Products.")

                addr1 = DeliveryAddress.objects.create(
                    customer=cust1,
                    name='Home Address',
                    address_line='123 Main St, New York, NY 10001',
                    phone_number='+1555123456',
                    is_default=True
                )
                addr2 = DeliveryAddress.objects.create(
                    customer=cust1,
                    name='Office Address',
                    address_line='789 Broadway, Floor 4, New York, NY 10003',
                    phone_number='+1555333222',
                    is_default=False
                )
                addr3 = DeliveryAddress.objects.create(
                    customer=cust2,
                    name='Default Home',
                    address_line='456 Oak Ave, Los Angeles, CA 90001',
                    phone_number='+1555987654',
                    is_default=True
                )

                o1 = Order.objects.create(
                    customer=cust1,
                    total_amount=108.49,
                    delivery_address=f"{addr1.name}: {addr1.address_line} (Tel: {addr1.phone_number})",
                    status='PENDING'
                )
                OrderItem.objects.create(order=o1, product=p2, product_name=p2.name, price=p2.price, quantity=1)
                OrderItem.objects.create(order=o1, product=p3, product_name=p3.name, price=p3.price, quantity=1)

                o2 = Order.objects.create(
                    customer=cust2,
                    rider=rider1,
                    total_amount=249.99,
                    delivery_address=f"{addr3.name}: {addr3.address_line} (Tel: {addr3.phone_number})",
                    status='RIDER_ASSIGNED'
                )
                OrderItem.objects.create(order=o2, product=p1, product_name=p1.name, price=p1.price, quantity=1)

                o3 = Order.objects.create(
                    customer=cust1,
                    rider=rider1,
                    total_amount=53.99,
                    delivery_address=f"{addr2.name}: {addr2.address_line} (Tel: {addr2.phone_number})",
                    status='DELIVERED'
                )
                OrderItem.objects.create(order=o3, product=p3, product_name=p3.name, price=p3.price, quantity=1)
                OrderItem.objects.create(order=o3, product=p4, product_name=p4.name, price=p4.price, quantity=1)

                o4 = Order.objects.create(
                    customer=cust2,
                    rider=rider1,
                    total_amount=42.00,
                    delivery_address=f"{addr3.name}: {addr3.address_line} (Tel: {addr3.phone_number})",
                    status='FAILED_DELIVERY',
                    failed_reason='Customer was not available at home after 3 phone call attempts.'
                )
                OrderItem.objects.create(order=o4, product=p5, product_name=p5.name, price=p5.price, quantity=1)

                self.stdout.write("Created Sample Orders.")
                self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Seeding failed: {str(e)}"))
