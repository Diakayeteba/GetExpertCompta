from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from businesses.models import BusinessProfile
from experts.models import ExpertProfile


@receiver(post_save, sender=User)
def create_role_profile(sender, instance: User, created: bool, **kwargs):
    if not created:
        return
    if instance.role == User.Role.BUSINESS:
        BusinessProfile.objects.get_or_create(
            user=instance,
            defaults={
                "company_name": instance.get_full_name() or instance.email.split("@")[0],
                "country": "CM",
            },
        )
    elif instance.role == User.Role.EXPERT:
        ExpertProfile.objects.get_or_create(
            user=instance,
            defaults={
                "title": "Expert-comptable",
                "country": "CM",
                "city": "",
            },
        )
