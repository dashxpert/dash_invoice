from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import (
    edit_payment_info,
    send_invoice_email,
    subscribe_newsletter,
    
)
from billing.views import razorpay_webhook,payment_page ,activate_plan_after_payment

urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('checkout/<int:tier_id>/', views.checkout_payment, name='checkout_payment'),
    path('buy/<int:tier_id>/', views.create_order, name='buy_tier'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('contact/', views.contact_view, name='contact'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_create, name='client_create'),
    path('invoices/add/', views.invoice_create, name='invoice_create'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('profile/payment-info/', edit_payment_info, name='edit_payment_info'),
    path('invoice/<int:invoice_id>/email/', send_invoice_email, name='send_invoice_email'),
    path('razorpay/webhook/', razorpay_webhook, name='razorpay_webhook'),
    path('subscribe/', subscribe_newsletter, name='subscribe'),
    path('invoices/<int:pk>/mark-paid/', views.mark_invoice_paid, name='mark_invoice_paid'),
    path('payment/<int:tier_id>/', views.payment_page, name='checkout_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/activate/', activate_plan_after_payment, name='activate_plan_after_payment'),

]

# ✅ STATIC MEDIA HANDLING (outside urlpatterns list)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
