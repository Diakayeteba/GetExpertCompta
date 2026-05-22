from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from accounts.models import User
from experts.models import ExpertProfile
from notifications.models import Notification
from requests_system.models import ServiceRequest
from reviews.models import Review

# Dashboard views for both Business and Expert users, with role-based access control and context data for the dashboard home page.
class RoleDashboardMixin(LoginRequiredMixin):
    login_url = reverse_lazy("account_login")

    def dispatch(self, request, *args, **kwargs): 
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if getattr(request.user, "role", None) == User.Role.ADMIN:
            return redirect("adminpanel:index")
        return super().dispatch(request, *args, **kwargs)

# Main dashboard home view that displays relevant information based on the user's role (Business or Expert).
class DashboardHomeView(RoleDashboardMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        role = getattr(u, "role", None)

        ctx["experts_preview"] = (
            ExpertProfile.objects.filter(verification_status=ExpertProfile.VerificationStatus.VERIFIED)
            .select_related("user")
            .prefetch_related("specialties")[:8]
        )
        ctx["notifications"] = Notification.objects.filter(user=u).order_by("-created_at")[:6]

        if role == User.Role.BUSINESS:
            bp = getattr(u, "business_profile", None)
            if bp:
                ctx["recent_requests"] = (
                    ServiceRequest.objects.filter(business=bp).select_related("business").order_by("-created_at")[:6]
                )
                ctx["stats"] = {
                    "requests_total": ServiceRequest.objects.filter(business=bp).count(),
                    "reviews_given": Review.objects.filter(business=bp).count(),
                }
        elif role == User.Role.EXPERT:
            ep = ExpertProfile.objects.filter(user=u).first()
            if ep:
                ctx["stats"] = {
                    "incoming_requests": ServiceRequest.objects.filter(expert_links__expert=ep).distinct().count(),
                    "rating": ep.average_rating,
                    "reviews": ep.review_count,
                }
                ctx["recent_request_links"] = (
                    ServiceRequest.objects.filter(expert_links__expert=ep)
                    .distinct()
                    .order_by("-created_at")[:6]
                )
        return ctx

# View for displaying user profile information, including business and expert profiles if they exist.
class ProfileView(RoleDashboardMixin, TemplateView):
    template_name = "dashboard/profile.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["business_profile"] = getattr(u, "business_profile", None)
        ctx["expert_profile"] = ExpertProfile.objects.filter(user=u).first()
        return ctx

# Mixin to restrict access to views only for users with the Expert role and an associated ExpertProfile.
class ExpertOnlyMixin(UserPassesTestMixin):
    login_url = reverse_lazy("account_login")

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if getattr(self.request.user, "role", None) != User.Role.EXPERT:
            return False
        return ExpertProfile.objects.filter(user=self.request.user).exists()

# View for managing expert availability status
class ExpertStatusView(RoleDashboardMixin, ExpertOnlyMixin, FormView):
    template_name = "dashboard/expert_status.html"
    success_url = reverse_lazy("dashboard:expert_status")

    def get_form_class(self):
        from dashboard.forms import ExpertAvailabilityForm

        return ExpertAvailabilityForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = ExpertProfile.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        from django.contrib import messages

        form.save()
        messages.success(self.request, "Votre statut de disponibilité a été mis à jour.")
        return super().form_valid(form)

# Redirect view for legacy expert availability URL to the new expert status page
class LegacyExpertAvailabilityRedirect(View):
    def get(self, request, *args, **kwargs):
        return redirect("dashboard:expert_status")
