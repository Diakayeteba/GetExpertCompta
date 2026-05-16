from django.urls import path

from core.views_discovery import DiscoveryExpertDetailView, DiscoveryExpertListView

app_name = "discovery"

urlpatterns = [
    path("", DiscoveryExpertListView.as_view(), name="expert_list"),
    path("expert/<int:pk>/", DiscoveryExpertDetailView.as_view(), name="expert_detail"),
]
