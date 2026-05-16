from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from businesses.models import BusinessProfile


class Plan(models.Model):
    class BillingPeriod(models.TextChoices):
        WEEKLY = "weekly", _("Hebdomadaire")
        MONTHLY = "monthly", _("Mensuel")
        QUARTERLY = "quarterly", _("Trimestriel")
        YEARLY = "yearly", _("Annuel")

    code = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    billing_period = models.CharField(max_length=20, choices=BillingPeriod.choices)
    amount_cents = models.PositiveIntegerField(help_text=_("Montant en plus petite unité (ex. centimes)."))
    currency = models.CharField(max_length=3, default="XOF")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("billing_period",)

    def __str__(self) -> str:
        return f"{self.name} ({self.get_billing_period_display()})"


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Actif")
        PAST_DUE = "past_due", _("Impayé")
        CANCELLED = "cancelled", _("Annulé")
        EXPIRED = "expired", _("Expiré")

    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    external_reference = models.CharField(max_length=128, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-started_at",)
        indexes = [
            models.Index(fields=["status", "current_period_end"]),
        ]

    def __str__(self) -> str:
        return f"{self.business} — {self.plan}"


class Invoice(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices")
    issued_at = models.DateTimeField(auto_now_add=True)
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="XOF")
    pdf = models.FileField(upload_to="invoices/%Y/%m/", blank=True, null=True)
    payment_reference = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ("-issued_at",)
