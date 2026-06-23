from django import forms
from .models import DeliveryAddress, Order

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['name', 'address_line', 'phone_number', 'is_default']
        widgets = {
            'address_line': forms.Textarea(attrs={'rows': 3, 'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'name': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'phone_number': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded'}),
        }

class OrderAddressUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
        }

class OrderFailForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['failed_reason']
        widgets = {
            'failed_reason': forms.Textarea(attrs={'rows': 3, 'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'placeholder': 'Enter reason for failed delivery...'}),
        }
        labels = {
            'failed_reason': 'Reason for Failure',
        }
