from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest

from core.models import AuditLog

logger = logging.getLogger("getexpertcompta.audit")

_VALID_ACTIONS = {c.value for c in AuditLog.Action}


def _client_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_audit_event(
    *,
    action: str,
    actor=None,
    object_type: str = "",
    object_id: str = "",
    object_repr: str = "",
    metadata: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
) -> AuditLog:
    """Crée une entrée d'audit (service centralisé)."""
    ua = ""
    ip = None
    if request is not None:
        ua = (request.META.get("HTTP_USER_AGENT") or "")[:2000]
        ip = _client_ip(request)
    if action not in _VALID_ACTIONS:
        action = AuditLog.Action.ADMIN_ACTION.value
    entry = AuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=str(object_id)[:64],
        object_repr=object_repr[:255],
        metadata=metadata or {},
        ip_address=ip,
        user_agent=ua,
    )
    logger.info("audit %s id=%s", action, entry.pk)
    return entry
