from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Client, Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]
    list_display = ('invoice_number', 'client', 'status', 'grand_total', 'date')
    list_filter = ('status', 'date')

admin.site.register(Client)
admin.site.register(Invoice, InvoiceAdmin)

from .models import PricingTier

admin.site.register(PricingTier)


from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'current_plan', 'mobile_number')
    search_fields = ('user__username', 'name', 'mobile_number')
