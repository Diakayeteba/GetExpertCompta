"""Zone découverte gratuite — liste, recherche, fiche expert (aperçu ou paywall)."""

from __future__ import annotations

from django.conf import settings
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView

from accounts.models import User
from experts.models import ExpertProfile
from subscriptions.services.entitlements import business_has_premium

from core.services.free_access import can_view_expert_full_profile, get_free_discovery_expert_ids


class DiscoveryExpertListView(ListView):
    """Liste et recherche d’experts vérifiés (catalogue public)."""

    model = ExpertProfile
    context_object_name = "experts"
    template_name = "discovery/expert_list.html"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            ExpertProfile.objects.filter(verification_status=ExpertProfile.VerificationStatus.VERIFIED)
            .select_related("user")
            .prefetch_related("specialties")
        )
        q = self.request.GET.get("q", "").strip()
        country = self.request.GET.get("country", "").strip()
        city = self.request.GET.get("city", "").strip()
        specialty = self.request.GET.get("specialty", "").strip()
        availability = self.request.GET.get("availability", "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(bio__icontains=q)
                | Q(city__icontains=q)
                | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__email__icontains=q)
            )
        if country:
            qs = qs.filter(country=country.upper()[:2])
        if city:
            qs = qs.filter(city__icontains=city)
        if specialty:
            qs = qs.filter(specialties__slug=specialty)
        if availability:
            qs = qs.filter(availability=availability)
        return qs.distinct().order_by("-average_rating", "-review_count")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["free_expert_ids"] = set(get_free_discovery_expert_ids())
        ctx["free_limit"] = getattr(settings, "FREE_DISCOVERY_EXPERT_LIMIT", 5)
        premium = False
        u = self.request.user
        if u.is_authenticated:
            role = getattr(u, "role", None)
            if role == User.Role.ADMIN:
                premium = True
            elif role == User.Role.BUSINESS:
                bp = getattr(u, "business_profile", None)
                premium = business_has_premium(bp)
        ctx["user_has_premium"] = premium
        q = self.request.GET.get("q", "").strip()
        ctx["show_premium_upsell"] = False
        if q and not premium:
            for e in ctx.get("experts", ()):
                if e.pk not in ctx["free_expert_ids"]:
                    ctx["show_premium_upsell"] = True
                    break
        return ctx


class DiscoveryExpertDetailView(DetailView):
    model = ExpertProfile
    context_object_name = "expert"
    template_name = "discovery/expert_detail.html"

    def get_queryset(self):
        return (
            ExpertProfile.objects.filter(verification_status=ExpertProfile.VerificationStatus.VERIFIED)
            .select_related("user")
            .prefetch_related("specialties")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        expert = self.object
        ctx["full_profile_access"] = can_view_expert_full_profile(user=self.request.user, expert_pk=expert.pk)
        ctx["premium_url"] = reverse_lazy("subscriptions:premium")
        ctx["checkout_url"] = reverse_lazy("subscriptions:checkout")
        return ctx
