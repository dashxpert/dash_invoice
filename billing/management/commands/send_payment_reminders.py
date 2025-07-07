from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from billing.models import Invoice
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Send payment reminders for unpaid invoices (Pro plan only)'

    def handle(self, *args, **kwargs):
        today = now().date()

        # Filter unpaid invoices with due date today or earlier, and reminder not sent
        invoices = Invoice.objects.filter(status='Unpaid', due_date__lte=today, reminder_sent=False)

        count = 0
        for invoice in invoices:
            user = invoice.user
            try:
                profile = user.userprofile
                if profile.current_plan.name.lower() == 'pro':
                    # Send reminder
                    send_mail(
                        subject=f'Payment Reminder - Invoice #{invoice.invoice_number}',
                        message=f'Dear {user.first_name},\n\nYour invoice #{invoice.invoice_number} is due. Please make the payment.',
                        from_email='noreply@dashxpert.com',
                        recipient_list=[invoice.client.email],
                        fail_silently=False,
                    )
                    invoice.reminder_sent = True
                    invoice.save()
                    count += 1
            except Exception as e:
                self.stderr.write(f"Error sending reminder for Invoice #{invoice.id}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f"{count} payment reminders sent."))
