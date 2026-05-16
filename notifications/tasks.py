from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from notifications.models import Notification


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_notification_email_task(self, notification_id: int) -> None:
    try:
        n = Notification.objects.select_related("user").get(pk=notification_id)
    except Notification.DoesNotExist:
        return
    try:
        send_mail(
            subject=n.title,
            message=n.body or n.title,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[n.user.email],
            fail_silently=settings.DEBUG,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
