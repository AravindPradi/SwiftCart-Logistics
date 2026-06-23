from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem, DeliveryAddress
from products.models import Product
from .forms import DeliveryAddressForm, OrderAddressUpdateForm
from django.db import transaction

@login_required
def cart_detail_view(request):
    if not request.user.is_customer():
        messages.error(request, "Only customers have access to the shopping cart.")
        return redirect('home')
    cart, created = Cart.objects.get_or_create(customer=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
def add_to_cart_view(request, product_id):
    if not request.user.is_customer():
        messages.error(request, "Only customers can order products.")
        return redirect('product_list')
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock_quantity <= 0:
        messages.error(request, f"Sorry, {product.name} is currently out of stock.")
        return redirect('product_list')

    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    try:
        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            qty = 1
    except ValueError:
        qty = 1

    if not item_created:
        new_qty = cart_item.quantity + qty
    else:
        new_qty = qty

    if new_qty > product.stock_quantity:
        messages.warning(request, f"Cannot add {qty} more. Only {product.stock_quantity} units available in stock.")
        if item_created:
            cart_item.delete()
        return redirect('cart')

    cart_item.quantity = new_qty
    cart_item.save()
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('cart')

@login_required
def update_cart_item_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    action = request.POST.get('action')
    product = cart_item.product

    if action == 'increase':
        if cart_item.quantity + 1 > product.stock_quantity:
            messages.warning(request, f"Cannot increase quantity. Only {product.stock_quantity} units available.")
        else:
            cart_item.quantity += 1
            cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity - 1 <= 0:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
            return redirect('cart')
        else:
            cart_item.quantity -= 1
            cart_item.save()
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
        return redirect('cart')
        
    return redirect('cart')

@login_required
def checkout_view(request):
    if not request.user.is_customer():
        messages.error(request, "Only customers can checkout.")
        return redirect('home')

    cart = get_object_or_404(Cart, customer=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('product_list')

    for item in cart.items.all():
        if item.quantity > item.product.stock_quantity:
            messages.error(request, f"Sorry, {item.product.name} is no longer available in the requested quantity (Only {item.product.stock_quantity} left).")
            return redirect('cart')

    addresses = DeliveryAddress.objects.filter(customer=request.user)
    
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        new_address = request.POST.get('new_address')
        phone_number = request.POST.get('phone_number')
        
        address_text = ""
        if address_id:
            addr = get_object_or_404(DeliveryAddress, id=address_id, customer=request.user)
            address_text = f"{addr.name}: {addr.address_line} (Tel: {addr.phone_number})"
        elif new_address:
            address_text = f"Custom Address: {new_address} (Tel: {phone_number})"
            if request.POST.get('save_address') == 'on':
                DeliveryAddress.objects.create(
                    customer=request.user,
                    name="Saved Address",
                    address_line=new_address,
                    phone_number=phone_number,
                    is_default=(not addresses.exists())
                )
        else:
            messages.error(request, "Please select or enter a delivery address.")
            return redirect('checkout')

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=request.user,
                    total_amount=cart.get_total_price(),
                    delivery_address=address_text,
                    status='PENDING'
                )

                for item in cart.items.all():
                    prod = item.product
                    if prod.stock_quantity < item.quantity:
                        raise ValueError(f"Insufficient stock for {prod.name}")
                    prod.stock_quantity -= item.quantity
                    prod.save()

                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        product_name=prod.name,
                        price=prod.price,
                        quantity=item.quantity
                    )
                
                cart.items.all().delete()

            messages.success(request, f"Order #{order.id} placed successfully!")
            return redirect('order_tracking', pk=order.id)

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('cart')
        except Exception as e:
            messages.error(request, "An error occurred while processing your order.")
            return redirect('cart')

    context = {
        'cart': cart,
        'addresses': addresses,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_tracking_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not (request.user == order.customer or request.user == order.rider or request.user.is_admin()):
        messages.error(request, "You are not authorized to view this order.")
        return redirect('home')

    form = None
    if request.user == order.customer and order.can_update_address():
        if request.method == 'POST':
            form = OrderAddressUpdateForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                messages.success(request, "Delivery address updated successfully.")
                return redirect('order_tracking', pk=order.pk)
        else:
            form = OrderAddressUpdateForm(instance=order)

    return render(request, 'orders/tracking.html', {'order': order, 'address_form': form})

@login_required
def address_list_view(request):
    if not request.user.is_customer():
        messages.error(request, "Only customers can manage addresses.")
        return redirect('home')
    addresses = DeliveryAddress.objects.filter(customer=request.user)
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.customer = request.user
            addr.save()
            messages.success(request, "Address added successfully.")
            return redirect('address_list')
    else:
        form = DeliveryAddressForm()
    return render(request, 'orders/address_list.html', {'addresses': addresses, 'form': form})

@login_required
def address_delete_view(request, pk):
    address = get_object_or_404(DeliveryAddress, pk=pk, customer=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('address_list')
