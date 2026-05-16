from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsExpertRole
from experts.models import ExpertProfile

from .serializers_expert import ExpertSelfSerializer


class ExpertSelfAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ExpertSelfSerializer
    permission_classes = [IsAuthenticated, IsExpertRole]

    def get_object(self) -> ExpertProfile:
        return ExpertProfile.objects.get(user=self.request.user)
