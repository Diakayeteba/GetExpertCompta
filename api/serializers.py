from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from businesses.models import BusinessProfile
from experts.models import ExpertProfile, Specialty
from notifications.models import Notification
from payments.models import PaymentTransaction
from requests_system.models import ServiceRequest, ServiceRequestAttachment, ServiceRequestExpert
from reviews.models import Review
from subscriptions.models import Plan, Subscription

User = get_user_model()


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ("id", "name", "slug")


class ExpertListSerializer(serializers.ModelSerializer):
    specialties = SpecialtySerializer(many=True, read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = ExpertProfile
        fields = (
            "id",
            "display_name",
            "title",
            "country",
            "city",
            "years_experience",
            "availability",
            "verification_status",
            "average_rating",
            "review_count",
            "specialties",
        )

    def get_display_name(self, obj: ExpertProfile) -> str:
        return obj.user.get_full_name() or obj.user.email


class ExpertDetailSerializer(ExpertListSerializer):
    bio = serializers.CharField(read_only=True)
    linkedin_url = serializers.URLField(read_only=True)

    class Meta(ExpertListSerializer.Meta):
        fields = ExpertListSerializer.Meta.fields + ("bio", "linkedin_url")


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = ("id", "company_name", "country", "city", "tax_id", "phone", "created_at")
        read_only_fields = ("id", "created_at")


class ServiceRequestExpertSerializer(serializers.ModelSerializer):
    expert_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequestExpert
        fields = ("id", "expert", "expert_name", "status", "responded_at")
        read_only_fields = ("responded_at",)

    def get_expert_name(self, obj: ServiceRequestExpert) -> str:
        u = obj.expert.user
        return u.get_full_name() or u.email


class ServiceRequestAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequestAttachment
        fields = ("id", "file", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class ServiceRequestSerializer(serializers.ModelSerializer):
    attachments = ServiceRequestAttachmentSerializer(many=True, read_only=True)
    expert_assignments = ServiceRequestExpertSerializer(source="expert_links", many=True, read_only=True)

    class Meta:
        model = ServiceRequest
        fields = (
            "id",
            "country",
            "accounting_needs",
            "status",
            "created_at",
            "attachments",
            "expert_assignments",
        )
        read_only_fields = ("status", "created_at")


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    expert_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = ServiceRequest
        fields = ("country", "accounting_needs", "expert_ids")

    def create(self, validated_data):
        expert_ids = validated_data.pop("expert_ids", [])
        business = self.context["business"]
        request = self.context["request"]
        sr = ServiceRequest.objects.create(
            business=business,
            created_by=request.user,
            status=ServiceRequest.Status.SUBMITTED,
            **validated_data,
        )
        for eid in expert_ids:
            ServiceRequestExpert.objects.get_or_create(
                service_request=sr,
                expert_id=eid,
                defaults={"status": ServiceRequestExpert.Status.INVITED},
            )
        return sr


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "service_request",
            "business",
            "expert",
            "rating",
            "comment",
            "moderation_status",
            "created_at",
        )
        read_only_fields = ("id", "moderation_status", "created_at", "business")

    def validate(self, attrs):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentification requise.")
        business = getattr(request.user, "business_profile", None)
        if business is None:
            raise serializers.ValidationError("Profil entreprise manquant.")
        sr = attrs.get("service_request")
        expert = attrs.get("expert")
        if sr and sr.business_id != business.pk:
            raise serializers.ValidationError({"service_request": "Cette demande n'appartient pas à votre entreprise."})
        if sr and expert:
            if not ServiceRequestExpert.objects.filter(
                service_request=sr,
                expert=expert,
                status=ServiceRequestExpert.Status.ACCEPTED,
            ).exists():
                raise serializers.ValidationError({"expert": "Interaction non vérifiée pour cet expert."})
        return attrs


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ("id", "code", "name", "billing_period", "amount_cents", "currency", "description", "is_active")


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.filter(is_active=True), source="plan", write_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "plan",
            "plan_id",
            "status",
            "started_at",
            "current_period_end",
            "cancel_at_period_end",
            "external_reference",
        )
        read_only_fields = ("status", "started_at", "current_period_end", "external_reference")


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = (
            "id",
            "provider",
            "status",
            "amount_cents",
            "currency",
            "external_id",
            "idempotency_key",
            "created_at",
        )
        read_only_fields = ("status", "external_id", "created_at")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "channel", "event_type", "title", "body", "payload", "read_at", "created_at")
        read_only_fields = ("id", "created_at")
