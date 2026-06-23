from django.db import models
from django.conf import settings
from products.models import Product

class DeliveryAddress(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_addresses')
    name = models.CharField(max_length=100, help_text="Label e.g. Home, Office")
    address_line = models.TextField()
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            DeliveryAddress.objects.filter(customer=self.customer).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.address_line[:30]}"

class Cart(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.customer.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RIDER_ASSIGNED', 'Rider Assigned'),
        ('REACHED_WAREHOUSE', 'Reached Warehouse'),
        ('PICKED_UP', 'Picked Up'),
        ('ON_THE_WAY', 'On The Way'),
        ('DELIVERED', 'Delivered'),
        ('FAILED_DELIVERY', 'Failed Delivery'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deliveries')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    failed_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_update_address(self):
        allowed_statuses = ['PENDING', 'RIDER_ASSIGNED', 'REACHED_WAREHOUSE']
        return self.status in allowed_statuses

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username} ({self.get_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order #{self.order.id}"
