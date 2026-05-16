from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import BusinessProfileAPIView
from api.views_expert import ExpertSelfAPIView
from payments.views_webhook import PaymentWebhookView
from api.viewsets import (
    ExpertProfileViewSet,
    NotificationViewSet,
    PaymentTransactionViewSet,
    PlanViewSet,
    ReviewViewSet,
    ServiceRequestViewSet,
    SubscriptionViewSet,
)

router = DefaultRouter()
router.register(r"experts", ExpertProfileViewSet, basename="expert")
router.register(r"requests", ServiceRequestViewSet, basename="request")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"plans", PlanViewSet, basename="plan")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")
router.register(r"payments", PaymentTransactionViewSet, basename="payment")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("business/profile/", BusinessProfileAPIView.as_view()),
    path("experts/me/", ExpertSelfAPIView.as_view()),
    path("payments/webhook/<str:provider>/", PaymentWebhookView.as_view()),
    path("", include(router.urls)),
]
