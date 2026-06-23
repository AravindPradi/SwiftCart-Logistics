from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomerRegisterForm, RiderRegisterForm, CustomerProfileForm, RiderProfileForm

def customer_register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You are now registered as a Customer.")
            login(request, user)
            return redirect('customer_dashboard')
    else:
        form = CustomerRegisterForm()
    return render(request, 'accounts/register_customer.html', {'form': form})

def rider_register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RiderRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You are now registered as a Rider.")
            login(request, user)
            return redirect('rider_dashboard')
    else:
        form = RiderRegisterForm()
    return render(request, 'accounts/register_rider.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    if user.is_customer():
        form_class = CustomerProfileForm
        template_name = 'accounts/profile_customer.html'
    elif user.is_rider():
        form_class = RiderProfileForm
        template_name = 'accounts/profile_rider.html'
    else:
        messages.info(request, "Admins manage profiles via Admin Panel.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = form_class(instance=user)

    return render(request, template_name, {'form': form})
