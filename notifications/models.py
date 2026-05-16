from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "in_app", _("Dans l'application")
        EMAIL = "email", _("E-mail")
        SMS = "sms", _("SMS")

    class EventType(models.TextChoices):
        REQUEST_RECEIVED = "request_received", _("Demande reçue")
        REQUEST_ACCEPTED = "request_accepted", _("Demande acceptée")
        SUBSCRIPTION_EXPIRING = "subscription_expiring", _("Abonnement bientôt expiré")
        PAYMENT_CONFIRMED = "payment_confirmed", _("Paiement confirmé")
        GENERIC = "generic", _("Générique")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.IN_APP)
    event_type = models.CharField(max_length=64, choices=EventType.choices, db_index=True)
    title = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "read_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} — {self.title}"
