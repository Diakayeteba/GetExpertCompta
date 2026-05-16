from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from core.services.audit import log_audit_event
from payments.models import PaymentTransaction
from payments.services.malitel import MalitelMoneyAdapter
from payments.services.orange import OrangeMoneyAdapter
from payments.services.wave import WaveAdapter
from subscriptions.models import Plan

User = get_user_model()

_ADAPTERS = {
    PaymentTransaction.Provider.ORANGE_MONEY: OrangeMoneyAdapter(),
    PaymentTransaction.Provider.WAVE: WaveAdapter(),
    PaymentTransaction.Provider.MALITEL_MONEY: MalitelMoneyAdapter(),
}


def initiate_payment(*, user: User, plan: Plan, provider: str, request: HttpRequest | None = None) -> PaymentTransaction:
    """Crée une transaction via l'adaptateur du fournisseur (couche d'abstraction)."""
    adapter = _ADAPTERS.get(provider)
    if adapter is None:
        raise ValueError("Fournisseur de paiement inconnu.")
    idem = uuid.uuid4().hex
    txn = adapter.initiate(user=user, plan=plan, idempotency_key=idem)
    log_audit_event(
        actor=user,
        action="payment",
        object_type="payment_transaction",
        object_id=str(txn.pk),
        object_repr=str(txn),
        request=request,
        metadata={"provider": provider, "plan_id": plan.pk},
    )
    return txn
