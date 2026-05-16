from pathlib import Path

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# En développement : enregistre les e-mails dans var/mail_outbox/ (fichiers .log) pour lecture locale.
# Surchargez EMAIL_BACKEND dans .env pour SMTP réel (Gmail, SendGrid, etc.).
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.filebased.EmailBackend",
)
EMAIL_FILE_PATH = env(
    "EMAIL_FILE_PATH",
    default=str(BASE_DIR / "var" / "mail_outbox"),
)
Path(EMAIL_FILE_PATH).mkdir(parents=True, exist_ok=True)

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost:8000"])

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:8000", "http://127.0.0.1:8000"],
)
