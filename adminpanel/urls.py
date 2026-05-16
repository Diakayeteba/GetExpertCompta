from django.urls import path

from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.AdminPanelIndexView.as_view(), name="index"),
]
