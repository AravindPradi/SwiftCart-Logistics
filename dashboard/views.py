from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.models import Product, Category
from products.forms import ProductForm, CategoryForm
from riders.models import RiderOrderAction
from django.db.models import Count, Sum, Q

User = get_user_model()

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('admin_dashboard')
        elif request.user.is_customer():
            return redirect('customer_dashboard')
        elif request.user.is_rider():
            return redirect('rider_dashboard')
    return render(request, 'home.html')

@login_required
def customer_dashboard_view(request):
    if not request.user.is_customer():
        messages.error(request, "Access Denied. Not a Customer.")
        return redirect('home')

    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    active_orders = orders.exclude(status__in=['DELIVERED', 'FAILED_DELIVERY', 'CANCELLED'])

    stats = {
        'total_orders': orders.count(),
        'active_orders': active_orders.count(),
        'total_spent': orders.filter(status='DELIVERED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00,
    }

    context = {
        'active_orders': active_orders[:5],
        'orders_history': orders[:10],
        'stats': stats,
    }
    return render(request, 'dashboard/customer_dashboard.html', context)

@login_required
def rider_dashboard_view(request):
    if not request.user.is_rider():
        messages.error(request, "Access Denied. Not a Rider.")
        return redirect('home')

    profile = request.user.rider_profile
    is_online = profile.is_online

    pending_orders = []
    active_deliveries = []

    if is_online:
        rejected_order_ids = RiderOrderAction.objects.filter(
            rider=request.user, action='REJECTED'
        ).values_list('order_id', flat=True)
        
        pending_orders = Order.objects.filter(
            status='PENDING'
        ).exclude(id__in=rejected_order_ids).order_by('-created_at')

        active_statuses = ['RIDER_ASSIGNED', 'REACHED_WAREHOUSE', 'PICKED_UP', 'ON_THE_WAY']
        active_deliveries = Order.objects.filter(
            rider=request.user, status__in=active_statuses
        ).order_by('-updated_at')

    context = {
        'profile': profile,
        'is_online': is_online,
        'pending_orders': pending_orders,
        'active_deliveries': active_deliveries,
    }
    return render(request, 'dashboard/rider_dashboard.html', context)

@login_required
def admin_dashboard_view(request):
    if not request.user.is_admin():
        messages.error(request, "Access Denied. Not an Admin.")
        return redirect('home')

    total_products = Product.objects.count()
    orders = Order.objects.all()
    total_orders = orders.count()
    pending_orders = orders.filter(status='PENDING').count()
    delivered_orders = orders.filter(status='DELIVERED').count()
    failed_deliveries = orders.filter(status='FAILED_DELIVERY').count()

    total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_riders = User.objects.filter(role=User.Role.RIDER).count()

    low_stock_products = Product.objects.filter(stock_quantity__lte=5, is_active=True)
    recent_orders = Order.objects.all().order_by('-created_at')[:8]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders_count': pending_orders,
        'delivered_orders_count': delivered_orders,
        'failed_deliveries_count': failed_deliveries,
        'total_customers': total_customers,
        'total_riders': total_riders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

# Admin CRUD - Products
@login_required
def admin_product_list(request):
    if not request.user.is_admin():
        return redirect('home')
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    cat_form = CategoryForm()
    if request.method == 'POST' and 'add_category' in request.POST:
        cat_form = CategoryForm(request.POST)
        if cat_form.is_valid():
            cat_form.save()
            messages.success(request, "Category added successfully.")
            return redirect('admin_products')

    context = {
        'products': products,
        'categories': categories,
        'cat_form': cat_form,
    }
    return render(request, 'dashboard/admin_products.html', context)

@login_required
def admin_product_create(request):
    if not request.user.is_admin():
        return redirect('home')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect('admin_products')
    else:
        form = ProductForm()
    return render(request, 'dashboard/admin_product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def admin_product_update(request, pk):
    if not request.user.is_admin():
        return redirect('home')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product {product.name} updated successfully.")
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/admin_product_form.html', {'form': form, 'product': product, 'title': 'Edit Product'})

@login_required
def admin_product_delete(request, pk):
    if not request.user.is_admin():
        return redirect('home')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
    return redirect('admin_products')

# Admin CRUD - Orders
@login_required
def admin_order_list(request):
    if not request.user.is_admin():
        return redirect('home')
    
    status_filter = request.GET.get('status')
    orders = Order.objects.all().order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)

    online_riders = User.objects.filter(role=User.Role.RIDER, rider_profile__is_online=True)

    context = {
        'orders': orders,
        'online_riders': online_riders,
        'status_filter': status_filter,
        'statuses': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/admin_orders.html', context)

@login_required
def admin_order_assign_rider(request, order_id):
    if not request.user.is_admin():
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        rider_id = request.POST.get('rider_id')
        if rider_id:
            rider = get_object_or_404(User, id=rider_id, role=User.Role.RIDER)
            order.rider = rider
            order.status = 'RIDER_ASSIGNED'
            order.save()
            messages.success(request, f"Rider {rider.username} assigned to Order #{order.id}.")
        else:
            messages.error(request, "Please select a rider.")
    return redirect('admin_orders')

@login_required
def admin_order_update_status(request, order_id):
    if not request.user.is_admin():
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            if status == 'FAILED_DELIVERY':
                order.failed_reason = request.POST.get('failed_reason', 'Cancelled by Admin')
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
        else:
            messages.error(request, "Invalid status choice.")
    return redirect('admin_orders')

# Admin CRUD - Riders
@login_required
def admin_rider_list(request):
    if not request.user.is_admin():
        return redirect('home')
    
    riders = User.objects.filter(role=User.Role.RIDER).select_related('rider_profile')
    
    rider_data = []
    for rider in riders:
        deliveries = Order.objects.filter(rider=rider)
        total = deliveries.count()
        success = deliveries.filter(status='DELIVERED').count()
        failed = deliveries.filter(status='FAILED_DELIVERY').count()
        
        success_rate = (success / (success + failed) * 100) if (success + failed) > 0 else 0
        
        rider_data.append({
            'rider': rider,
            'total_deliveries': total,
            'success_deliveries': success,
            'failed_deliveries': failed,
            'success_rate': round(success_rate, 1),
        })

    return render(request, 'dashboard/admin_riders.html', {'riders': rider_data})

# Admin CRUD - Customers
@login_required
def admin_customer_list(request):
    if not request.user.is_admin():
        return redirect('home')
    
    customers = User.objects.filter(role=User.Role.CUSTOMER).select_related('customer_profile')
    
    customer_data = []
    for customer in customers:
        orders = Order.objects.filter(customer=customer)
        total_orders = orders.count()
        total_spent = orders.filter(status='DELIVERED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
        
        customer_data.append({
            'customer': customer,
            'total_orders': total_orders,
            'total_spent': total_spent,
        })
        
    return render(request, 'dashboard/admin_customers.html', {'customers': customer_data})
