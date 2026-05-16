from celery import shared_task
from django.utils import timezone

from notifications.models import Notification
from notifications.services.notify import notify_user
from subscriptions.models import Subscription


@shared_task
def notify_subscriptions_expiring_soon() -> int:
    """Alerte les entreprises dont l'abonnement expire dans 3 jours."""
    from datetime import timedelta

    horizon = timezone.now() + timedelta(days=3)
    qs = Subscription.objects.filter(
        status=Subscription.Status.ACTIVE,
        current_period_end__lte=horizon,
        current_period_end__gte=timezone.now(),
    ).select_related("business__user")
    count = 0
    for sub in qs:
        notify_user(
            user=sub.business.user,
            event_type=Notification.EventType.SUBSCRIPTION_EXPIRING,
            title="Votre abonnement premium arrive à échéance",
            body="Renouvelez pour conserver l'accès illimité aux experts.",
            payload={"subscription_id": sub.pk},
            email_async=True,
        )
        count += 1
    return count
