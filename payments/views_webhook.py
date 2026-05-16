"""Réception des webhooks paiement (validation de signature à compléter par opérateur)."""

from __future__ import annotations

import hashlib
import hmac
import json

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services.audit import log_audit_event
from payments.models import PaymentTransaction, PaymentWebhookLog


@method_decorator(csrf_exempt, name="dispatch")
class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, provider: str):
        raw_body = request.body
        payload = json.loads(raw_body.decode("utf-8") or "{}")
        digest = hashlib.sha256(raw_body).hexdigest()
        signature = request.headers.get("X-Signature", "")
        secret = getattr(settings, "PAYMENT_WEBHOOK_SECRETS", {}).get(provider, "")
        valid = False
        if not secret and settings.DEBUG:
            valid = True
        elif secret and signature:
            expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
            valid = hmac.compare_digest(expected, signature)
        log = PaymentWebhookLog.objects.create(
            provider=provider,
            signature_valid=valid,
            payload_hash=digest,
            payload=payload,
            processed=False,
            error_message="" if valid else "Signature invalide ou secrète manquante",
        )
        log_audit_event(
            actor=None,
            action="payment",
            object_type="payment_webhook",
            object_id=str(log.pk),
            object_repr=provider,
            request=request,
            metadata={"valid": valid},
        )
        if not valid:
            return Response({"status": "rejected"}, status=400)
        log.processed = True
        log.save(update_fields=["processed"])
        return Response({"status": "ok"})
