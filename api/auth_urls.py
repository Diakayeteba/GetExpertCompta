from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from api.viewsets import ThrottledTokenObtainPairView, ThrottledTokenRefreshView

urlpatterns = [
    path("", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", ThrottledTokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
]
