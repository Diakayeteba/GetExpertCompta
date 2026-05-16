from decimal import Decimal

from django.db.models import Avg, Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from experts.models import ExpertProfile
from reviews.models import Review


@receiver(post_save, sender=Review)
def refresh_expert_rating(sender, instance: Review, **kwargs):
    agg = Review.objects.filter(
        expert=instance.expert,
        moderation_status=Review.ModerationStatus.APPROVED,
    ).aggregate(avg=Avg("rating"), cnt=Count("id"))

    avg = agg["avg"] or Decimal("0")
    ExpertProfile.objects.filter(pk=instance.expert_id).update(
        average_rating=avg,
        review_count=agg["cnt"] or 0,
    )
