from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin/Warehouse'
        CUSTOMER = 'CUSTOMER', 'Customer'
        RIDER = 'RIDER', 'Rider'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_rider(self):
        return self.role == self.Role.RIDER

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Customer Profile for {self.user.username}"

class RiderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rider_profile')
    phone_number = models.CharField(max_length=15)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        status = "Online" if self.is_online else "Offline"
        return f"Rider Profile for {self.user.username} ({status})"
