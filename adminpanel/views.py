from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from accounts.models import User
from businesses.models import BusinessProfile
from experts.models import ExpertProfile
from payments.models import PaymentTransaction
from reviews.models import Review
from subscriptions.models import Subscription


class AdminPanelAccessMixin(UserPassesTestMixin):
    login_url = reverse_lazy("account_login")

    def test_func(self):
        u = self.request.user
        return bool(u.is_authenticated and getattr(u, "role", None) == User.Role.ADMIN)


class AdminPanelIndexView(LoginRequiredMixin, AdminPanelAccessMixin, TemplateView):
    template_name = "adminpanel/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "count_users": User.objects.count(),
                "count_experts": ExpertProfile.objects.count(),
                "count_businesses": BusinessProfile.objects.count(),
                "count_pending_experts": ExpertProfile.objects.filter(
                    verification_status=ExpertProfile.VerificationStatus.PENDING
                ).count(),
                "count_subscriptions": Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
                "count_payments": PaymentTransaction.objects.count(),
                "count_reviews_pending": Review.objects.filter(moderation_status=Review.ModerationStatus.PENDING).count(),
            }
        )
        return ctx
