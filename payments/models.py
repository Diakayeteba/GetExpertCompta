from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from subscriptions.models import Subscription


class PaymentTransaction(models.Model):
    class Provider(models.TextChoices):
        ORANGE_MONEY = "orange_money", _("Orange Money")
        WAVE = "wave", _("Wave")
        MALITEL_MONEY = "malitel_money", _("Malitel Money")
        INTERNAL = "internal", _("Interne / test")

    class Status(models.TextChoices):
        PENDING = "pending", _("En attente")
        AUTHORIZED = "authorized", _("Autorisé")
        CAPTURED = "captured", _("Encaissé")
        FAILED = "failed", _("Échoué")
        REFUNDED = "refunded", _("Remboursé")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payment_transactions",
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_transactions",
    )
    provider = models.CharField(max_length=32, choices=Provider.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="XOF")
    external_id = models.CharField(max_length=191, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=64, blank=True, db_index=True)
    raw_request = models.JSONField(default=dict, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["provider", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="uniq_payment_idempotency_when_set",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.provider} {self.amount_cents/100:.2f} {self.currency} ({self.status})"


class PaymentWebhookLog(models.Model):
    provider = models.CharField(max_length=32, choices=PaymentTransaction.Provider.choices)
    signature_valid = models.BooleanField(default=False)
    payload_hash = models.CharField(max_length=128, db_index=True)
    payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False, db_index=True)
    error_message = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    related_transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhook_logs",
    )

    class Meta:
        ordering = ("-received_at",)
