from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'gst_number', 'address']


# forms.py


from django import forms
from .models import Invoice, InvoiceItem, Client
from django.forms.models import inlineformset_factory

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'due_date', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # 👈 Extract the logged-in user
        super().__init__(*args, **kwargs)

        if user:
            # ✅ Only show clients created by this user
            self.fields['client'].queryset = Client.objects.filter(user=user)



InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    fields=['description', 'quantity', 'unit_price', 'tax_rate'],
    extra=1,
    can_delete=True
)


from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'name',
            'mobile_number',
            'profile_picture',
            'custom_logo',  # ✅ Added for Pro Plan users
            'bank_account_name',
            'bank_account_number',
            'ifsc_code',
            'upi_id',
        ]



from .models import UserProfile
# ✅ CORRECTED FORM (optional if you need a shorter version)
class PaymentInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'bank_account_name',
            'bank_account_number',
            'ifsc_code',
            'upi_id',
        ]

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile  # Adjust path if needed

class RegistrationForm(forms.ModelForm):
    mobile_number = forms.CharField(max_length=15, label="Mobile Number")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


from django import forms
from .models import NewsletterSubscriber

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
