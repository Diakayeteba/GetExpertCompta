from django.urls import path

from core import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("how-it-works/", views.HowItWorksView.as_view(), name="how_it_works"),
    path("pricing/", views.PricingView.as_view(), name="pricing"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
