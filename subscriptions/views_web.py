from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from accounts.models import User
from subscriptions.forms import DemoSubscriptionForm
from subscriptions.models import Plan
from subscriptions.services.demo_checkout import activate_demo_subscription


class PremiumLandingView(TemplateView):
    """Page marketing Premium + accès au tunnel de souscription."""

    template_name = "subscriptions/premium.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["plans"] = Plan.objects.filter(is_active=True).order_by("amount_cents")
        return ctx


class SubscriptionCheckoutView(LoginRequiredMixin, FormView):
    template_name = "subscriptions/checkout.html"
    form_class = DemoSubscriptionForm
    success_url = reverse_lazy("subscriptions:checkout_success")
    login_url = reverse_lazy("account_login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if getattr(request.user, "role", None) != User.Role.BUSINESS:
            messages.error(request, "La souscription Premium est réservée aux comptes entreprise.")
            return HttpResponseRedirect(reverse_lazy("dashboard:index"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        plan = form.cleaned_data["plan"]
        provider = form.cleaned_data["provider"]
        activate_demo_subscription(user=self.request.user, plan=plan, provider=provider, request=self.request)
        messages.success(
            self.request,
            "Votre abonnement Premium (démonstration) est activé. Les paiements réels seront branchés sur les opérateurs.",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["plans"] = Plan.objects.filter(is_active=True)
        return ctx

    def get_initial(self):
        initial = super().get_initial()
        pid = self.request.GET.get("plan")
        if pid and Plan.objects.filter(pk=pid, is_active=True).exists():
            initial["plan"] = pid
        return initial


class SubscriptionSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "subscriptions/checkout_success.html"
    login_url = reverse_lazy("account_login")
