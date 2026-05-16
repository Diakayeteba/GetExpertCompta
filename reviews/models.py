from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from businesses.models import BusinessProfile
from experts.models import ExpertProfile
from requests_system.models import ServiceRequest, ServiceRequestExpert


class Review(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING = "pending", _("En attente")
        APPROVED = "approved", _("Approuvé")
        REJECTED = "rejected", _("Rejeté")

    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="review",
    )
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="reviews")
    expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("avis")
        verbose_name_plural = _("avis")
        indexes = [
            models.Index(fields=["expert", "moderation_status"]),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        link = ServiceRequestExpert.objects.filter(
            service_request=self.service_request,
            expert=self.expert,
            status=ServiceRequestExpert.Status.ACCEPTED,
        ).exists()
        if not link:
            raise ValidationError(_("Avis autorisé uniquement après interaction vérifiée (demande acceptée)."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
