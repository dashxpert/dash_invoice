from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from billing.models import PricingTier  # ✅ Import the plan model
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # ✅ Assign 'Free' plan by default
        free_plan = PricingTier.objects.filter(name__iexact='Free').first()
        UserProfile.objects.create(user=instance, current_plan=free_plan)
    else:
        instance.userprofile.save()
