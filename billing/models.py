from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)  # Assuming 'Client' model exists
    invoice_number = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    reminder_sent = models.BooleanField(default=False) 
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Required to check monthly limits

    def __str__(self):
        return f"Invoice {self.invoice_number}"



class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def total_price(self):
        return self.quantity * self.unit_price

    def tax_value(self):
        return self.total_price() * (self.tax_rate / 100)

    def __str__(self):
        return self.description


from django.db.models.signals import pre_save
from django.dispatch import receiver

def generate_invoice_number():
    last_invoice = Invoice.objects.order_by('-id').first()
    if last_invoice:
        num = int(last_invoice.invoice_number.replace('INV', '')) + 1
    else:
        num = 1
    return f"INV{num:04d}"

@receiver(pre_save, sender=Invoice)
def set_invoice_number(sender, instance, **kwargs):
    if not instance.invoice_number:
        instance.invoice_number = generate_invoice_number()


from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 🪙 Subscription Plan
    current_plan = models.ForeignKey('billing.PricingTier', on_delete=models.SET_NULL, null=True, blank=True)

    # 👤 Personal Info
    name = models.CharField(max_length=100, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # 🖼️ Custom Logo (Pro Plan Only)
    custom_logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    # 🏦 Bank Details
    bank_account_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username



class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PricingTier(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    features = models.TextField()
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# billing/models.py
from django.contrib.auth.models import User
from django.db import models

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='created')  # created, success, failed
    created_at = models.DateTimeField(auto_now_add=True)



from django.db import models
from django.contrib.auth.models import User

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
