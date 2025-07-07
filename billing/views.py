from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.template.loader import get_template
from django.db import transaction
from django.db.models import Q
from datetime import datetime

from xhtml2pdf import pisa

from .models import Client, Invoice, UserProfile
from .forms import (
    ClientForm,
    InvoiceForm,
    InvoiceItemFormSet,
    UserProfileForm,
)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models  # ✅ this line is required


def home(request):
    total_clients = Client.objects.count()
    total_invoices = Invoice.objects.count()
    total_revenue = Invoice.objects.aggregate(total=models.Sum('grand_total'))['total'] or 0
    sample_clients = [
        {
            "name": "Ravi Sharma",
            "profession": "Web Developer",
            "rating": "⭐️⭐️⭐️⭐️⭐️",
            "email": "ravi.dev@example.com",
            "photo_url": "https://i.pravatar.cc/150?img=3"
        },
        {
            "name": "Ananya Mehta",
            "profession": "Content Strategist",
            "rating": "⭐️⭐️⭐️⭐️½",
            "email": "ananya.writer@example.com",
            "photo_url": "https://i.pravatar.cc/150?img=6"
        },
        {
            "name": "Karan Verma",
            "profession": "Digital Marketer",
            "rating": "⭐️⭐️⭐️⭐️",
            "email": "karan.ads@example.com",
            "photo_url": "https://i.pravatar.cc/150?img=12"
        }
    ]

    return render(request, 'billing/home.html', {
        'total_clients': total_clients,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'sample_clients': sample_clients
    })


# 👥 Clients
@login_required
def client_list(request):
    clients = Client.objects.filter(user=request.user)
    return render(request, 'billing/client_list.html', {'clients': clients})


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'billing/client_form.html', {'form': form})


from django.contrib import messages
from django.utils.timezone import now
from django.db import transaction
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from billing.models import Invoice
from .models import UserProfile  # Adjust if placed elsewhere
from .forms import InvoiceForm, InvoiceItemFormSet

@login_required
def invoice_create(request):
    user = request.user
    today = now()

    # ✅ Safely fetch user profile and plan
    try:
        user_profile = user.userprofile
        current_plan = user_profile.current_plan
        plan_name = current_plan.name.lower() if current_plan else "free"
    except Exception:
        messages.error(request, "⚠️ Unable to determine your current plan. Please contact support.")
        return redirect('home')

    # ✅ Apply Free plan restriction: 3 invoices/month
    if plan_name == "free" and not user.is_superuser:
        invoice_count = Invoice.objects.filter(
            user=user,
            created_at__year=today.year,
            created_at__month=today.month
        ).count()

        if invoice_count >= 3:
            messages.warning(request, "❌ Free plan allows only 3 invoices/month. Please upgrade.")
            return redirect('pricing')

    # ✅ Handle form submission
    if request.method == 'POST':
        form = InvoiceForm(request.POST, user=request.user)  # ✅ Pass user here
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.user = user

                total, tax = 0, 0
                for item_form in formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                        qty = item_form.cleaned_data['quantity']
                        price = item_form.cleaned_data['unit_price']
                        rate = item_form.cleaned_data['tax_rate']
                        total += qty * price
                        tax += (qty * price) * (rate / 100)

                invoice.total_amount = total
                invoice.tax_amount = tax
                invoice.grand_total = total + tax
                invoice.save()

                formset.instance = invoice
                formset.save()

            messages.success(request, "✅ Invoice created successfully.")
            return redirect('invoice_list')

    else:
        form = InvoiceForm(user=request.user)  # ✅ Pass user here
        formset = InvoiceItemFormSet()

    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'formset': formset,
    })




# 📃 Invoice List
@login_required
def invoice_list(request):
    invoices = Invoice.objects.filter(user=request.user)
    client_id = request.GET.get('client')
    status = request.GET.get('status')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')

    if client_id:
        invoices = invoices.filter(client__id=client_id)
    if status:
        invoices = invoices.filter(status=status)
    if date_from:
        invoices = invoices.filter(date__gte=date_from)
    if date_to:
        invoices = invoices.filter(date__lte=date_to)

    clients = Client.objects.filter(user=request.user)
    return render(request, 'billing/invoice_list.html', {
        'invoices': invoices,
        'clients': clients,
    })



from django.template.loader import get_template
from xhtml2pdf import pisa  # if using for PDF

# 🧾 Invoice Detail
@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    profile = request.user.userprofile
    plan = profile.current_plan.name.lower() if profile.current_plan else "free"

    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'show_watermark': plan == "free",
        'custom_logo_url': profile.custom_logo.url if plan == "pro" and profile.custom_logo else None,
    })


from django.templatetags.static import static
from django.conf import settings
import os

def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        return os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return uri


# views.py
from django.conf import settings
import os

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)

    logo_path = None
    if invoice.user.userprofile.current_plan.name.lower() == 'pro' and invoice.user.userprofile.custom_logo:
        logo_path = os.path.join(settings.MEDIA_ROOT, str(invoice.user.userprofile.custom_logo))

    context = {
        'invoice': invoice,
        'user': request.user,
        'custom_logo_path': logo_path,  # ✅ Pass local image path
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'

    template = get_template('billing/invoice_pdf.html')
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    return response




# ⚙️ Edit Payment Info / Profile
@login_required
def edit_payment_info(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'billing/edit_payment_info.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from .forms import RegistrationForm
from billing.models import PricingTier
from .models import NewsletterSubscriber  # optional if using newsletter app

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            mobile_number = form.cleaned_data['mobile_number']

            # ✅ Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "⚠️ Email is already registered.")
                return redirect('register')

            # ✅ Create user
            user = User.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )

            # ✅ Assign default plan (Free)
            free_plan = PricingTier.objects.filter(name__iexact="Free").first()

            # ✅ Create user profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': f"{first_name} {last_name}",
                    'mobile_number': mobile_number,
                    'current_plan': free_plan,
                }
            )

            # ✅ Link to existing newsletter subscriber (if any)
            from newsletter.models import NewsletterSubscriber  # Optional
            try:
                subscriber = NewsletterSubscriber.objects.get(email=email)
                subscriber.user = user
                subscriber.save()
            except NewsletterSubscriber.DoesNotExist:
                pass

            messages.success(request, "✅ Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'auth/register.html', {'form': form})




# 🔐 Custom Login (with Remember Me)
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(60 * 60 * 24 * 7)
        return super().form_valid(form)


# 🔐 Logout
def custom_logout_view(request):
    logout(request)
    return redirect('home')


from .models import Blog

def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'billing/blog_list.html', {'blogs': blogs})


def contact_view(request):
    return render(request, 'billing/contact.html')



from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Invoice, Client


def user_dashboard(request):
    user = request.user
    invoices = Invoice.objects.filter(user=user)
    user_profile = user.userprofile

    # ✅ KPI Metrics
    total_clients = Client.objects.filter(user=user).count()
    total_invoices = invoices.count()
    total_revenue = invoices.aggregate(total=Sum('grand_total'))['total'] or 0
    current_plan = user_profile.current_plan.name if user_profile.current_plan else 'Free'

    # ✅ Month-wise Revenue Chart
    monthly_data = (
        invoices.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('grand_total'))
        .order_by('month')
    )

    months = [entry['month'].strftime('%b %Y') for entry in monthly_data]
    totals = [float(entry['total']) if entry['total'] else 0 for entry in monthly_data]

    # ✅ Paid vs Unpaid Pie Chart
    paid = invoices.filter(status='paid').aggregate(total=Sum('grand_total'))['total'] or 0
    unpaid = invoices.filter(status='unpaid').aggregate(total=Sum('grand_total'))['total'] or 0

    paid_revenue = float(paid)
    unpaid_revenue = float(unpaid)

    context = {
        'months': months,
        'totals': totals,
        'total_clients': total_clients,
        'total_invoices': total_invoices,
        'total_revenue': float(total_revenue),
        'current_plan': current_plan,
        'paid_revenue': paid_revenue,
        'unpaid_revenue': unpaid_revenue,
    }

    return render(request, 'billing/user_dashboard.html', context)



import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from billing.models import PricingTier
from .models import UserProfile

# Razorpay Client Initialization
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# ✅ Step 1: Show Razorpay Checkout Page
@login_required
def payment_page(request, tier_id):
    try:
        selected_plan = PricingTier.objects.get(id=tier_id)
    except PricingTier.DoesNotExist:
        messages.error(request, "❌ Selected plan does not exist.")
        return redirect('pricing')

    amount_in_paise = int(selected_plan.price * 100)
    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': 1,
    }

    razorpay_order = client.order.create(data=order_data)

    # Save plan temporarily in session for later reference
    request.session['selected_tier_id'] = selected_plan.id

    return render(request, 'billing/payment.html', {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': razorpay_order['id'],
        'amount': selected_plan.price,
        'currency': 'INR',
        'plan_name': selected_plan.name,
    })


# ✅ Step 2: Razorpay's JS handler calls this
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        return JsonResponse({"status": "success"})

    return HttpResponseBadRequest("Invalid request")


# ✅ Step 3: Final Plan Activation on GET request
@login_required
def activate_plan_after_payment(request):
    tier_id = request.session.get('selected_tier_id')

    if not tier_id:
        messages.error(request, "⚠️ Plan ID missing. Please try again.")
        return redirect('pricing')

    try:
        selected_plan = PricingTier.objects.get(id=tier_id)
        profile = request.user.userprofile
        profile.current_plan = selected_plan
        profile.save()
        messages.success(request, f"🎉 {selected_plan.name} plan activated!")
        del request.session['selected_tier_id']
    except PricingTier.DoesNotExist:
        messages.error(request, "❌ Plan does not exist.")
    except Exception as e:
        messages.error(request, f"⚠️ Error: {str(e)}")

    return redirect('home')




# billing/views.py
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from .models import PricingTier, Payment

def pricing_view(request):
    tiers = PricingTier.objects.exclude(name="Agency")  # Show only 3 plans
    return render(request, 'billing/pricing.html', {'tiers': tiers, 'razorpay_key': settings.RAZORPAY_KEY_ID})

def create_order(request, tier_id):
    tier = PricingTier.objects.get(id=tier_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    amount = int(tier.price * 100)  # ₹ to paise
    razorpay_order = client.order.create(dict(amount=amount, currency='INR', payment_capture='1'))

    payment = Payment.objects.create(
        user=request.user,
        order_id=razorpay_order['id'],
        amount=tier.price
    )

    return render(request, 'payment_checkout.html', {
        'tier': tier,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount
    })


# billing/views.py
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        tier_id = request.POST.get('tier_id')

        # Step 1: Verify Razorpay Signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
        except razorpay.errors.SignatureVerificationError:
            return HttpResponse("❌ Signature verification failed!", status=400)

        # Step 2: Mark payment as successful
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.payment_id = payment_id
            payment.status = 'success'
            payment.save()

            # Optional: Update user’s subscription tier here

            return render(request, 'payment_success.html', {'payment': payment})
        except Payment.DoesNotExist:
            return HttpResponse("Payment record not found.", status=400)



import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from billing.models import PricingTier

def checkout_payment(request, tier_id):
    if not request.user.is_authenticated:
        return redirect('login')

    tier = get_object_or_404(PricingTier, id=tier_id)
    amount_in_paise = int(tier.price * 100)

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create order
    order = client.order.create({
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': '1'
    })

    return render(request, 'payment_checkout.html', {
        'tier': tier,
        'amount': amount_in_paise,
        'razorpay_order_id': order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID
    })


from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from .models import Invoice

def send_invoice_email(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)

        # ✅ Check if user has allowed plan
        allowed_plans = ["Starter", "Pro"]
        user_plan = getattr(request.user.userprofile.current_plan, 'name', None)

        if user_plan not in allowed_plans:
            return HttpResponse("❌ This feature is available only for Starter or Pro users.", status=403)

        # ✅ Render invoice to PDF
        html = render_to_string('billing/invoice_pdf.html', {
            'invoice': invoice,
            'user': request.user
        })
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buffer)
        if pisa_status.err:
            return HttpResponse("❌ Failed to generate PDF.", status=500)

        pdf = buffer.getvalue()

        # ✅ Send email
        email = EmailMessage(
            subject=f"Invoice #{invoice.invoice_number} from Dashxpert",
            body=(
                f"Hi {invoice.client.name},\n\n"
                f"Please find attached the invoice #{invoice.invoice_number} from Dashxpert.\n\n"
                "Thank you for your business!\n\n"
                "- Team Dashxpert"
            ),
            from_email=settings.EMAIL_HOST_USER,
            to=[invoice.client.email],
        )
        email.attach(f"Invoice_{invoice.invoice_number}.pdf", pdf, "application/pdf")
        email.send()

        return render(request, 'billing/email_success.html', {
            'invoice': invoice
        })

    except Invoice.DoesNotExist:
        return HttpResponse("❌ Invoice not found.", status=404)

    except Exception as e:
        return HttpResponse(f"❌ Failed to send email: {str(e)}", status=500)



# revisit again to upgrade from free to plan
# views.py
import hmac
import hashlib
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from billing.models import PricingTier
from .models import UserProfile
from django.contrib.auth.models import User

@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        received_data = request.body
        signature = request.headers.get('X-Razorpay-Signature')

        # ✅ Verify signature
        generated_signature = hmac.new(
            webhook_secret.encode(), received_data, hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(generated_signature, signature):
            payload = json.loads(received_data)

            # ✅ Check payment successful event
            if payload.get("event") == "payment.captured":
                email = payload["payload"]["payment"]["entity"].get("email")
                amount = payload["payload"]["payment"]["entity"].get("amount") / 100  # in INR
                notes = payload["payload"]["payment"]["entity"].get("notes", {})

                plan_name = notes.get("plan")  # e.g., 'Pro', 'Business'
                if email and plan_name:
                    try:
                        user = User.objects.get(email=email)
                        profile = user.userprofile
                        new_plan = PricingTier.objects.get(name__iexact=plan_name)
                        profile.current_plan = new_plan
                        profile.save()
                        return JsonResponse({"status": "success", "message": "Plan upgraded."})
                    except User.DoesNotExist:
                        return JsonResponse({"error": "User not found"}, status=404)
                    except PricingTier.DoesNotExist:
                        return JsonResponse({"error": "Plan not found"}, status=404)
            return JsonResponse({"status": "ignored"})
        else:
            return JsonResponse({"error": "Invalid signature"}, status=403)

    return JsonResponse({"error": "Invalid method"}, status=405)



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterForm
from .models import NewsletterSubscriber

def subscribe_newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, "🎉 Subscribed successfully!")
            else:
                messages.info(request, "✅ You're already subscribed.")
            return redirect('home')  # or wherever you want to redirect
    else:
        form = NewsletterForm()

    return render(request, "newsletter/subscribe.html", {"form": form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from billing.models import Invoice

@login_required
def mark_invoice_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    invoice.status = 'Paid'
    invoice.reminder_sent = False  # reset if needed
    invoice.save()
    return redirect('invoice_detail', pk=pk)
