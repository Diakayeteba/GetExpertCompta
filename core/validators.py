"""Validateurs de fichiers pour téléversements sécurisés."""

from __future__ import annotations

import os
from typing import BinaryIO

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_upload_file(f: BinaryIO, *, filename: str) -> None:
    """Vérifie extension, taille et type MIME (magic) pour limiter les risques."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError("Extension de fichier non autorisée.")

    data = f.read(settings.FILE_UPLOAD_MAX_MEMORY_SIZE + 1)
    if len(data) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("Fichier trop volumineux.")
    f.seek(0)

    mime = None
    try:
        import magic

        mime = magic.from_buffer(data[:2048], mime=True)
    except Exception:
        mime = None
    if mime is None:
        if not settings.DEBUG:
            raise ValidationError("Impossible de vérifier le type MIME du fichier.")
        return
    if mime not in settings.ALLOWED_UPLOAD_MIME_TYPES:
        raise ValidationError("Type de fichier non autorisé.")
