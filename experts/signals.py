from django.db.models.signals import post_save
from django.dispatch import receiver

from core.services.free_access import invalidate_free_discovery_cache
from experts.models import ExpertProfile


@receiver(post_save, sender=ExpertProfile)
def expert_profile_changed(sender, **kwargs):
    invalidate_free_discovery_cache()
