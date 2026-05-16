from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from notifications.services.notify import notify_user
from requests_system.models import ServiceRequestExpert


@receiver(post_save, sender=ServiceRequestExpert)
def notify_expert_on_invitation(sender, instance: ServiceRequestExpert, created: bool, **kwargs):
    if not created or instance.status != ServiceRequestExpert.Status.INVITED:
        return
    notify_user(
        user=instance.expert.user,
        event_type=Notification.EventType.REQUEST_RECEIVED,
        title="Nouvelle demande de service",
        body=f"Vous avez été sélectionné pour la demande #{instance.service_request_id}.",
        payload={"service_request_id": instance.service_request_id},
        email_async=True,
    )
