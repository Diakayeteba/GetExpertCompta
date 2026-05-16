from __future__ import annotations

from django.contrib.auth import get_user_model

from notifications.models import Notification
from notifications.tasks import send_notification_email_task

User = get_user_model()


def notify_user(
    *,
    user: User,
    event_type: str,
    title: str,
    body: str = "",
    payload: dict | None = None,
    channel: str = Notification.Channel.IN_APP,
    email_async: bool = False,
) -> Notification:
    """Crée une notification in-app ; enfile un e-mail si demandé."""
    n = Notification.objects.create(
        user=user,
        channel=channel,
        event_type=event_type,
        title=title,
        body=body,
        payload=payload or {},
    )
    if email_async:
        send_notification_email_task.delay(n.pk)
    return n
