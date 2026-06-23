from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/customer/', views.customer_dashboard_view, name='customer_dashboard'),
    path('dashboard/rider/', views.rider_dashboard_view, name='rider_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Admin Product Management
    path('dashboard/admin/products/', views.admin_product_list, name='admin_products'),
    path('dashboard/admin/products/create/', views.admin_product_create, name='admin_product_create'),
    path('dashboard/admin/products/<int:pk>/update/', views.admin_product_update, name='admin_product_update'),
    path('dashboard/admin/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
    
    # Admin Order Management
    path('dashboard/admin/orders/', views.admin_order_list, name='admin_orders'),
    path('dashboard/admin/orders/<int:order_id>/assign/', views.admin_order_assign_rider, name='admin_order_assign_rider'),
    path('dashboard/admin/orders/<int:order_id>/update-status/', views.admin_order_update_status, name='admin_order_update_status'),
    
    # Admin Rider & Customer lists
    path('dashboard/admin/riders/', views.admin_rider_list, name='admin_riders'),
    path('dashboard/admin/customers/', views.admin_customer_list, name='admin_customers'),
]
