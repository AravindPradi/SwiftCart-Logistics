from django.contrib import admin
from .models import DeliveryAddress, Cart, CartItem, Order, OrderItem

admin.site.register(DeliveryAddress)
admin.site.register(Cart)
admin.site.register(CartItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'rider', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'rider__username']
    inlines = [OrderItemInline]
