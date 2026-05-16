from __future__ import annotations

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.models import User
from businesses.models import BusinessProfile
from core.permissions import IsBusinessRole
from experts.models import ExpertProfile
from notifications.models import Notification
from payments.models import PaymentTransaction
from payments.services.orchestrator import initiate_payment
from requests_system.models import ServiceRequest
from reviews.models import Review
from subscriptions.models import Plan, Subscription
from subscriptions.services.entitlements import business_has_premium

from core.services.free_access import can_view_expert_full_profile

from .serializers import (
    ExpertDetailSerializer,
    ExpertListSerializer,
    NotificationSerializer,
    PaymentTransactionSerializer,
    PlanSerializer,
    ReviewSerializer,
    ServiceRequestCreateSerializer,
    ServiceRequestSerializer,
    SubscriptionSerializer,
)


def _expert_catalog_full_access(user) -> bool:
    if not user.is_authenticated:
        return False
    if getattr(user, "role", None) == User.Role.ADMIN:
        return True
    if getattr(user, "role", None) == User.Role.BUSINESS:
        profile = getattr(user, "business_profile", None)
        return bool(profile and business_has_premium(profile))
    return False


class ExpertProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ExpertProfile.objects.filter(verification_status=ExpertProfile.VerificationStatus.VERIFIED).select_related(
        "user"
    ).prefetch_related("specialties")
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            pk = self.kwargs.get(self.lookup_field or "pk")
            if pk is not None:
                try:
                    expert_pk = int(pk)
                except (TypeError, ValueError):
                    return ExpertListSerializer
                if can_view_expert_full_profile(user=self.request.user, expert_pk=expert_pk):
                    return ExpertDetailSerializer
        return ExpertListSerializer

    def get_queryset(self):
        return (
            ExpertProfile.objects.filter(verification_status=ExpertProfile.VerificationStatus.VERIFIED)
            .select_related("user")
            .prefetch_related("specialties")
        )

    def filter_queryset(self, queryset):
        qs = queryset
        params = self.request.query_params
        if country := params.get("country"):
            qs = qs.filter(country=country)
        if city := params.get("city"):
            qs = qs.filter(city__icontains=city)
        if specialty := params.get("specialty"):
            qs = qs.filter(specialties__slug=specialty)
        if availability := params.get("availability"):
            qs = qs.filter(availability=availability)
        if min_rating := params.get("min_rating"):
            qs = qs.filter(average_rating__gte=min_rating)
        if min_years := params.get("min_years"):
            qs = qs.filter(years_experience__gte=min_years)
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(bio__icontains=search)
                | Q(city__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
            )
        qs = qs.order_by("-average_rating", "-review_count").distinct()
        if not _expert_catalog_full_access(self.request.user):
            limit = getattr(settings, "FREE_DISCOVERY_EXPERT_LIMIT", settings.FREE_TIER_EXPERT_PREVIEW_LIMIT)
            ids = list(qs.values_list("pk", flat=True)[:limit])
            qs = ExpertProfile.objects.filter(pk__in=ids).select_related("user").prefetch_related("specialties")
            qs = qs.order_by("-average_rating", "-review_count")
        return qs


class ServiceRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBusinessRole]
    throttle_scope = "burst"

    def get_queryset(self):
        business = get_object_or_404(BusinessProfile, user=self.request.user)
        return (
            ServiceRequest.objects.filter(business=business)
            .prefetch_related("attachments", "expert_links")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ServiceRequestCreateSerializer
        return ServiceRequestSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.request.user.is_authenticated:
            ctx["business"] = get_object_or_404(BusinessProfile, user=self.request.user)
        return ctx

    def perform_create(self, serializer):
        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsBusinessRole]

    def get_queryset(self):
        business = get_object_or_404(BusinessProfile, user=self.request.user)
        return Review.objects.filter(business=business)

    def perform_create(self, serializer):
        business = get_object_or_404(BusinessProfile, user=self.request.user)
        serializer.save(business=business)


class PlanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsBusinessRole]

    def get_queryset(self):
        business = get_object_or_404(BusinessProfile, user=self.request.user)
        return Subscription.objects.filter(business=business).select_related("plan")


class PaymentTransactionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated, IsBusinessRole]
    throttle_scope = "burst"

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        plan_id = request.data.get("plan_id")
        provider = request.data.get("provider")
        if not plan_id or not provider:
            raise ValidationError({"detail": "plan_id et provider sont requis."})
        plan = get_object_or_404(Plan, pk=plan_id, is_active=True)
        txn = initiate_payment(user=request.user, plan=plan, provider=provider, request=request)
        ser = self.get_serializer(txn)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class NotificationViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        if notif.user_id != request.user.id:
            raise PermissionDenied()
        notif.read_at = timezone.now()
        notif.save(update_fields=["read_at"])
        return Response(self.get_serializer(notif).data)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
