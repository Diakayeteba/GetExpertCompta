from urllib.parse import quote

from django.conf import settings

from accounts.models import User
from experts.models import ExpertProfile
from subscriptions.services.entitlements import business_has_premium


def platform(request):
    """Variables globales d’UI (Premium, limites gratuites, avatar)."""
    ctx = {
        "FREE_DISCOVERY_EXPERT_LIMIT": getattr(settings, "FREE_DISCOVERY_EXPERT_LIMIT", 5),
        "FREE_TIER_EXPERT_PREVIEW_LIMIT": getattr(settings, "FREE_TIER_EXPERT_PREVIEW_LIMIT", 5),
        "user_has_premium": False,
        "user_avatar_url": None,
    }
    u = request.user
    if not u.is_authenticated:
        return ctx

    role = getattr(u, "role", None)
    if role == User.Role.ADMIN:
        ctx["user_has_premium"] = True
    elif role == User.Role.BUSINESS:
        bp = getattr(u, "business_profile", None)
        ctx["user_has_premium"] = business_has_premium(bp) if bp else False

    ep = ExpertProfile.objects.filter(user=u).first()
    if ep and ep.avatar:
        ctx["user_avatar_url"] = ep.avatar.url
    else:
        label = quote((u.get_full_name() or u.email or "User")[:48])
        ctx["user_avatar_url"] = (
            f"https://ui-avatars.com/api/?name={label}&background=047857&color=fff&size=128"
        )
    return ctx
