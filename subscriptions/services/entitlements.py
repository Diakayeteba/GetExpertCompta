from __future__ import annotations

from django.utils import timezone

from businesses.models import BusinessProfile
from subscriptions.models import Subscription


def business_has_premium(business: BusinessProfile | None) -> bool:
    """Premium actif si un abonnement est en cours de validité."""
    if business is None:
        return False
    now = timezone.now()
    return Subscription.objects.filter(
        business=business,
        status=Subscription.Status.ACTIVE,
        current_period_end__gt=now,
    ).exists()
