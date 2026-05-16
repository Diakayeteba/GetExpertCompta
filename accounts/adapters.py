from allauth.account.adapter import DefaultAccountAdapter
from django import forms
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger("getexpertcompta.mail")


class RoleAccountAdapter(DefaultAccountAdapter):
    """Allauth : impose le rôle à l'inscription et synchronise le username."""

    def send_mail(self, template_prefix: str, email: str, context: dict) -> None:
        try:
            super().send_mail(template_prefix, email, context)
        except Exception:
            logger.exception("Échec d'envoi e-mail allauth (%s) → %s", template_prefix, email)
            raise

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        role = getattr(form, "cleaned_data", {}).get("role")
        if role not in (User.Role.BUSINESS, User.Role.EXPERT):
            raise forms.ValidationError("Rôle d'inscription invalide.")
        user.role = role
        user.username = user.email
        if commit:
            user.save()
        return user
