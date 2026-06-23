from django.db import models
from django.conf import settings
from orders.models import Order

class RiderOrderAction(models.Model):
    ACTION_CHOICES = [
        ('REJECTED', 'Rejected'),
    ]
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rider_actions')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='rider_actions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='REJECTED')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rider', 'order')

    def __str__(self):
        return f"Rider {self.rider.username} {self.action} Order #{self.order.id}"
