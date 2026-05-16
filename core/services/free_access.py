"""Règles d’accès catalogue gratuit vs Premium (découverte publique)."""

from __future__ import annotations

from django.conf import settings
from django.core.cache import cache

from experts.models import ExpertProfile
from subscriptions.services.entitlements import business_has_premium

_CACHE_KEY = "getexpertcompta:free_discovery_expert_pks"
_CACHE_TTL = 300


def invalidate_free_discovery_cache() -> None:
    cache.delete(_CACHE_KEY)


def get_free_discovery_expert_ids() -> list[int]:
    """Identifiants des experts « inclus » dans la version gratuite (aperçu complet)."""
    cached = cache.get(_CACHE_KEY)
    if cached is not None:
        return list(cached)
    limit = getattr(settings, "FREE_DISCOVERY_EXPERT_LIMIT", 5)
    qs = (
        ExpertProfile.objects.filter(verification_status=ExpertProfile.VerificationStatus.VERIFIED)
        .order_by("-average_rating", "-review_count", "pk")
        .values_list("pk", flat=True)[:limit]
    )
    pks = list(qs)
    cache.set(_CACHE_KEY, pks, _CACHE_TTL)
    return pks


def can_view_expert_full_profile(*, user, expert_pk: int) -> bool:
    """Premium business, admin, ou expert dans le pool gratuit."""
    if not user.is_authenticated:
        return int(expert_pk) in set(get_free_discovery_expert_ids())
    role = getattr(user, "role", None)
    from accounts.models import User

    if role == User.Role.ADMIN:
        return True
    if role == User.Role.EXPERT:
        ep = getattr(user, "expert_profile", None)
        if ep and ep.pk == int(expert_pk):
            return True
        return int(expert_pk) in set(get_free_discovery_expert_ids())
    if role == User.Role.BUSINESS:
        bp = getattr(user, "business_profile", None)
        if business_has_premium(bp):
            return True
        return int(expert_pk) in set(get_free_discovery_expert_ids())
    return False
