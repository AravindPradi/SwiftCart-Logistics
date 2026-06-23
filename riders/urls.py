from django.urls import path
from . import views

urlpatterns = [
    path('toggle-availability/', views.toggle_availability_view, name='toggle_availability'),
    path('accept/<int:order_id>/', views.accept_order_view, name='accept_order'),
    path('reject/<int:order_id>/', views.reject_order_view, name='reject_order'),
    path('update-status/<int:order_id>/', views.update_status_view, name='update_status'),
    path('accepted/', views.rider_accepted_orders_view, name='rider_accepted_orders'),
]
