from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Journal d'audit append-only pour actions sensibles."""

    class Action(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Connexion réussie"
        LOGIN_FAILURE = "login_failure", "Échec connexion"
        LOGOUT = "logout", "Déconnexion"
        USER_CREATE = "user_create", "Création utilisateur"
        USER_UPDATE = "user_update", "Mise à jour utilisateur"
        EXPERT_VERIFY = "expert_verify", "Vérification expert"
        PAYMENT = "payment", "Paiement"
        SUBSCRIPTION = "subscription", "Abonnement"
        REQUEST = "request", "Demande de service"
        REVIEW_MODERATION = "review_moderation", "Modération avis"
        FILE_UPLOAD = "file_upload", "Téléversement fichier"
        ADMIN_ACTION = "admin_action", "Action administrateur"

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64, choices=Action.choices, db_index=True)
    object_type = models.CharField(max_length=128, blank=True)
    object_id = models.CharField(max_length=64, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Entrée d'audit"
        verbose_name_plural = "Journal d'audit"
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["object_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} @ {self.created_at:%Y-%m-%d %H:%M}"
