from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="index"),
    path("profil/", views.ProfileView.as_view(), name="profile"),
    path("expert/statut/", views.ExpertStatusView.as_view(), name="expert_status"),
    path("expert/availability/", views.LegacyExpertAvailabilityRedirect.as_view(), name="expert_availability"),
]
