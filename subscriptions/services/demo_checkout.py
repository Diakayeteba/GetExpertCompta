"""Activation d’abonnement en mode démo (prêt pour branchement PSP réel)."""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from core.services.audit import log_audit_event
from payments.models import PaymentTransaction
from subscriptions.models import Invoice, Plan, Subscription

User = get_user_model()


def _period_delta(plan: Plan) -> timedelta:
    return {
        Plan.BillingPeriod.WEEKLY: timedelta(days=7),
        Plan.BillingPeriod.MONTHLY: timedelta(days=30),
        Plan.BillingPeriod.QUARTERLY: timedelta(days=91),
        Plan.BillingPeriod.YEARLY: timedelta(days=365),
    }.get(plan.billing_period, timedelta(days=30))


@transaction.atomic
def activate_demo_subscription(
    *,
    user: User,
    plan: Plan,
    provider: str,
    request=None,
) -> tuple[Subscription, PaymentTransaction]:
    """Crée une transaction « encaissée » et un abonnement actif (démonstration)."""
    if getattr(user, "role", None) != User.Role.BUSINESS:
        raise ValueError("Seuls les comptes entreprise peuvent souscrire.")
    business = user.business_profile
    now = timezone.now()
    end = now + _period_delta(plan)

    sub = Subscription.objects.create(
        business=business,
        plan=plan,
        status=Subscription.Status.ACTIVE,
        started_at=now,
        current_period_end=end,
        cancel_at_period_end=False,
        external_reference=f"DEMO-{provider}-{plan.code}",
        metadata={"mode": "demo", "provider": provider},
    )
    txn = PaymentTransaction.objects.create(
        user=user,
        subscription=sub,
        provider=provider,
        status=PaymentTransaction.Status.CAPTURED,
        amount_cents=plan.amount_cents,
        currency=plan.currency,
        external_id=f"DEMO-{sub.pk}",
        raw_request={"plan": plan.code},
        raw_response={"status": "captured", "demo": True},
    )
    Invoice.objects.create(
        subscription=sub,
        amount_cents=plan.amount_cents,
        currency=plan.currency,
        payment_reference=txn.external_id,
    )
    log_audit_event(
        actor=user,
        action="subscription",
        object_type="subscription",
        object_id=str(sub.pk),
        object_repr=str(sub),
        request=request,
        metadata={"provider": provider, "demo": True},
    )
    from core.services.free_access import invalidate_free_discovery_cache

    invalidate_free_discovery_cache()
    return sub, txn
