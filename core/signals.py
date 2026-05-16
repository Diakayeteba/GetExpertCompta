import logging

from django.contrib.auth import signals as auth_signals
from django.dispatch import receiver

from core.services.audit import log_audit_event

logger = logging.getLogger("getexpertcompta.security")


@receiver(auth_signals.user_logged_in)
def audit_user_logged_in(sender, request, user, **kwargs):
    log_audit_event(
        actor=user,
        action="login_success",
        object_type="user",
        object_id=str(user.pk),
        object_repr=user.email,
        request=request,
    )


@receiver(auth_signals.user_logged_out)
def audit_user_logged_out(sender, request, user, **kwargs):
    if user is not None:
        log_audit_event(
            actor=user,
            action="logout",
            object_type="user",
            object_id=str(user.pk),
            object_repr=user.email,
            request=request,
        )


@receiver(auth_signals.user_login_failed)
def audit_user_login_failed(sender, credentials, request, **kwargs):
    ident = ""
    if isinstance(credentials, dict):
        ident = str(credentials.get("username") or credentials.get("email") or "")
    log_audit_event(
        actor=None,
        action="login_failure",
        object_type="session",
        object_id="",
        object_repr=ident[:255],
        request=request,
        metadata={"credentials_keys": list(credentials.keys()) if isinstance(credentials, dict) else []},
    )
