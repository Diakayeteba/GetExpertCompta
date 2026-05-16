from __future__ import annotations

from django.contrib.auth import get_user_model

from payments.models import PaymentTransaction
from subscriptions.models import Plan

User = get_user_model()


class WaveAdapter:
    code = PaymentTransaction.Provider.WAVE

    def initiate(self, *, user: User, plan: Plan, idempotency_key: str) -> PaymentTransaction:
        return PaymentTransaction.objects.create(
            user=user,
            provider=self.code,
            status=PaymentTransaction.Status.PENDING,
            amount_cents=plan.amount_cents,
            currency=plan.currency,
            idempotency_key=idempotency_key,
            raw_request={"plan_code": plan.code, "adapter": "wave"},
        )
