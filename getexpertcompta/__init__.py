"""GetExpertCompta Django project package."""

try:
    from .celery import app as celery_app
except ImportError:  # pragma: no cover - environnement sans Celery installé
    celery_app = None  # type: ignore[misc, assignment]

__all__ = ("celery_app",)
