from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Specialty(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        verbose_name = _("spécialité")
        verbose_name_plural = _("spécialités")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


def expert_document_upload(instance: "ExpertDocument", filename: str) -> str:
    return f"experts/{instance.expert_profile_id}/documents/{filename}"


def expert_avatar_upload(instance: "ExpertProfile", filename: str) -> str:
    return f"experts/{instance.pk}/avatar/{filename}"


class ExpertProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "pending", _("En attente")
        VERIFIED = "verified", _("Vérifié")
        REJECTED = "rejected", _("Rejeté")

    class Availability(models.TextChoices):
        AVAILABLE = "available", _("Disponible")
        OCCUPIED = "occupied", _("Occupé")
        UNAVAILABLE = "unavailable", _("Indisponible")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expert_profile",
    )
    title = models.CharField(max_length=180)
    country = models.CharField(max_length=2, db_index=True)
    city = models.CharField(max_length=120, db_index=True, blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    specialties = models.ManyToManyField(Specialty, related_name="experts", blank=True)
    linkedin_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
    )
    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.UNAVAILABLE,
        db_index=True,
    )
    avatar = models.ImageField(upload_to=expert_avatar_upload, blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil expert")
        verbose_name_plural = _("profils experts")
        indexes = [
            models.Index(fields=["country", "city", "availability"]),
            models.Index(fields=["verification_status", "availability"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.email} ({self.country})"


class ExpertDocument(models.Model):
    class DocumentType(models.TextChoices):
        IDENTITY = "identity", _("Pièce d'identité")
        CERTIFICATION = "certification", _("Certification")
        PROFESSIONAL = "professional", _("Justificatif professionnel")
        CV = "cv", _("CV")
        OTHER = "other", _("Autre")

    expert_profile = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=32, choices=DocumentType.choices)
    file = models.FileField(upload_to=expert_document_upload)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploaded_at",)
        verbose_name = _("document expert")
        verbose_name_plural = _("documents experts")
