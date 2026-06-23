from django.urls import path
from . import views

urlpatterns = [
    path('register/customer/', views.customer_register_view, name='register_customer'),
    path('register/rider/', views.rider_register_view, name='register_rider'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
