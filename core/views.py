"""Vues utilitaires, santé et pages publiques."""

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class HealthCheckView(View):
    """Point de terminaison minimal pour orchestrateurs (Docker, K8s)."""

    def get(self, request):
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        payload = {
            "status": "ok" if db_ok else "degraded",
            "database": "up" if db_ok else "down",
            "debug": settings.DEBUG,
        }
        status = 200 if db_ok else 503
        return JsonResponse(payload, status=status)


class HomeView(TemplateView):
    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from experts.models import ExpertProfile

        limit = getattr(settings, "FREE_DISCOVERY_EXPERT_LIMIT", settings.FREE_TIER_EXPERT_PREVIEW_LIMIT)
        ctx["free_discovery_limit"] = limit
        ctx["experts_preview"] = (
            ExpertProfile.objects.filter(verification_status=ExpertProfile.VerificationStatus.VERIFIED)
            .select_related("user")
            .prefetch_related("specialties")
            .order_by("-average_rating", "-review_count")[:limit]
        )
        return ctx


class HowItWorksView(TemplateView):
    template_name = "public/how_it_works.html"


class PricingView(TemplateView):
    template_name = "public/pricing.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from subscriptions.models import Plan

        ctx["plans"] = Plan.objects.filter(is_active=True)
        return ctx


class FaqView(TemplateView):
    template_name = "public/faq.html"


class ContactView(TemplateView):
    template_name = "public/contact.html"
