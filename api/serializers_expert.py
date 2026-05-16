from rest_framework import serializers

from experts.models import ExpertProfile


class ExpertSelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertProfile
        fields = (
            "id",
            "title",
            "country",
            "city",
            "years_experience",
            "bio",
            "linkedin_url",
            "availability",
            "verification_status",
        )
        read_only_fields = ("id", "verification_status")
