from django.urls import path

from subscriptions.views_web import PremiumLandingView, SubscriptionCheckoutView, SubscriptionSuccessView

app_name = "subscriptions"

urlpatterns = [
    path("", PremiumLandingView.as_view(), name="premium"),
    path("souscrire/", SubscriptionCheckoutView.as_view(), name="checkout"),
    path("merci/", SubscriptionSuccessView.as_view(), name="checkout_success"),
]
