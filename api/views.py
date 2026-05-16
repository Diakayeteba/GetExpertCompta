from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from businesses.models import BusinessProfile
from core.permissions import IsBusinessRole

from .serializers import BusinessProfileSerializer


class BusinessProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated, IsBusinessRole]

    def get_object(self):
        return BusinessProfile.objects.get(user=self.request.user)
