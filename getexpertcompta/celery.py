"""Celery application instance for background tasks."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "getexpertcompta.settings.development")

app = Celery("getexpertcompta")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
