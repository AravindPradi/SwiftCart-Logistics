from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_detail_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('track/<int:pk>/', views.order_tracking_view, name='order_tracking'),
    path('addresses/', views.address_list_view, name='address_list'),
    path('addresses/<int:pk>/delete/', views.address_delete_view, name='address_delete'),
]
