from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("L'adresse e-mail est obligatoire."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", "business")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields["role"] = "admin"
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Utilisateur unique avec rôle RBAC (admin, entreprise, expert)."""

    class Role(models.TextChoices):
        ADMIN = "admin", _("Administrateur")
        BUSINESS = "business", _("Entreprise")
        EXPERT = "expert", _("Expert-comptable")

    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(_("adresse e-mail"), unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, db_index=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")
        indexes = [
            models.Index(fields=["role", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
