from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile, RiderProfile

User = get_user_model()

class CustomerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                address=self.cleaned_data.get('address')
            )
        return user

class RiderRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.RIDER
        if commit:
            user.save()
            RiderProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                is_online=False
            )
        return user

class CustomerProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'customer_profile'):
            profile = self.instance.customer_profile
            self.fields['phone_number'].initial = profile.phone_number
            self.fields['address'].initial = profile.address

    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'customer_profile'):
            profile = user.customer_profile
            profile.phone_number = self.cleaned_data.get('phone_number')
            profile.address = self.cleaned_data.get('address')
            if commit:
                profile.save()
        return user

class RiderProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'rider_profile'):
            profile = self.instance.rider_profile
            self.fields['phone_number'].initial = profile.phone_number

    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'rider_profile'):
            profile = user.rider_profile
            profile.phone_number = self.cleaned_data.get('phone_number')
            if commit:
                profile.save()
        return user
