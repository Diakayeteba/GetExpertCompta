from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BusinessProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_profile",
    )
    company_name = models.CharField(max_length=255)
    country = models.CharField(max_length=2, db_index=True)
    city = models.CharField(max_length=120, blank=True)
    tax_id = models.CharField(max_length=64, blank=True, help_text=_("Identifiant fiscal (chiffré au repos si activé)."))
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil entreprise")
        verbose_name_plural = _("profils entreprises")

    def __str__(self) -> str:
        return self.company_name
