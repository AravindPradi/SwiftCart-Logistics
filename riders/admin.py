from django.contrib import admin
from .models import RiderOrderAction

@admin.register(RiderOrderAction)
class RiderOrderActionAdmin(admin.ModelAdmin):
    list_display = ['rider', 'order', 'action', 'timestamp']
    list_filter = ['action']
