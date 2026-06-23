from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from .models import RiderOrderAction
from orders.forms import OrderFailForm
from django.db import transaction

@login_required
def toggle_availability_view(request):
    if not request.user.is_rider():
        messages.error(request, "Only riders can perform this action.")
        return redirect('home')
    
    profile = request.user.rider_profile
    profile.is_online = not profile.is_online
    profile.save()
    status_str = "online" if profile.is_online else "offline"
    messages.success(request, f"You are now {status_str}.")
    return redirect('rider_dashboard')

@login_required
def accept_order_view(request, order_id):
    if not request.user.is_rider():
        messages.error(request, "Only riders can accept orders.")
        return redirect('home')

    profile = request.user.rider_profile
    if not profile.is_online:
        messages.error(request, "You must be online to accept orders.")
        return redirect('rider_dashboard')

    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            if order.status != 'PENDING':
                messages.error(request, "This order has already been accepted by another rider.")
                return redirect('rider_dashboard')
            
            if RiderOrderAction.objects.filter(rider=request.user, order=order, action='REJECTED').exists():
                messages.error(request, "You have already rejected this order.")
                return redirect('rider_dashboard')

            order.rider = request.user
            order.status = 'RIDER_ASSIGNED'
            order.save()
            messages.success(request, f"Order #{order.id} accepted successfully!")
            return redirect('rider_accepted_orders')
            
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('rider_dashboard')

@login_required
def reject_order_view(request, order_id):
    if not request.user.is_rider():
        messages.error(request, "Only riders can reject orders.")
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, status='PENDING')
    
    RiderOrderAction.objects.get_or_create(
        rider=request.user,
        order=order,
        action='REJECTED'
    )
    messages.info(request, f"Order #{order.id} rejected. It will no longer appear on your dashboard.")
    return redirect('rider_dashboard')

@login_required
def update_status_view(request, order_id):
    if not request.user.is_rider():
        messages.error(request, "Only riders can perform this action.")
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, rider=request.user)

    if order.status == 'DELIVERED':
        messages.error(request, "Delivered orders cannot be updated.")
        return redirect('rider_accepted_orders')

    next_status = request.POST.get('status')
    
    valid_transitions = {
        'RIDER_ASSIGNED': ['REACHED_WAREHOUSE'],
        'REACHED_WAREHOUSE': ['PICKED_UP'],
        'PICKED_UP': ['ON_THE_WAY'],
        'ON_THE_WAY': ['DELIVERED', 'FAILED_DELIVERY'],
        'FAILED_DELIVERY': []
    }

    current_options = valid_transitions.get(order.status, [])
    
    if next_status not in current_options:
        messages.error(request, "Invalid status transition.")
        return redirect('rider_accepted_orders')

    if next_status == 'FAILED_DELIVERY':
        if request.method == 'POST' and request.POST.get('failed_reason'):
            form = OrderFailForm(request.POST, instance=order)
            if form.is_valid():
                fail_order = form.save(commit=False)
                fail_order.status = 'FAILED_DELIVERY'
                fail_order.save()
                messages.success(request, f"Order #{order.id} marked as Failed Delivery.")
                return redirect('rider_accepted_orders')
            else:
                return render(request, 'riders/fail_order.html', {'form': form, 'order': order})
        else:
            form = OrderFailForm(instance=order)
            return render(request, 'riders/fail_order.html', {'form': form, 'order': order})
    else:
        order.status = next_status
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")

    return redirect('rider_accepted_orders')

@login_required
def rider_accepted_orders_view(request):
    if not request.user.is_rider():
        messages.error(request, "Only riders have access to this page.")
        return redirect('home')

    active_statuses = ['RIDER_ASSIGNED', 'REACHED_WAREHOUSE', 'PICKED_UP', 'ON_THE_WAY']
    active_deliveries = Order.objects.filter(rider=request.user, status__in=active_statuses).order_by('-updated_at')
    completed_deliveries = Order.objects.filter(rider=request.user, status__in=['DELIVERED', 'FAILED_DELIVERY']).order_by('-updated_at')

    context = {
        'active_deliveries': active_deliveries,
        'completed_deliveries': completed_deliveries,
    }
    return render(request, 'riders/accepted_orders.html', context)
