from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from businesses.models import BusinessProfile
from experts.models import ExpertProfile


def request_attachment_upload(instance: "ServiceRequestAttachment", filename: str) -> str:
    return f"requests/{instance.service_request_id}/{filename}"


class ServiceRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Brouillon")
        SUBMITTED = "submitted", _("Soumise")
        IN_PROGRESS = "in_progress", _("En cours")
        CLOSED = "closed", _("Clôturée")
        CANCELLED = "cancelled", _("Annulée")

    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="service_requests")
    country = models.CharField(max_length=2)
    accounting_needs = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_service_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    experts = models.ManyToManyField(
        ExpertProfile,
        through="ServiceRequestExpert",
        related_name="service_requests",
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("demande de service")
        verbose_name_plural = _("demandes de service")


class ServiceRequestAttachment(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=request_attachment_upload)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploaded_at",)


class ServiceRequestExpert(models.Model):
    class Status(models.TextChoices):
        INVITED = "invited", _("Invité")
        ACCEPTED = "accepted", _("Accepté")
        DECLINED = "declined", _("Refusé")

    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="expert_links")
    expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INVITED, db_index=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("service_request", "expert")
        verbose_name = _("affectation expert")
        verbose_name_plural = _("affectations experts")
