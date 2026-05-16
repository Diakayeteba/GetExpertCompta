from __future__ import annotations

from typing import Protocol

from django.contrib.auth import get_user_model

from payments.models import PaymentTransaction
from subscriptions.models import Plan

User = get_user_model()


class PaymentProviderAdapter(Protocol):
    code: str

    def initiate(self, *, user: User, plan: Plan, idempotency_key: str) -> PaymentTransaction:
        ...
