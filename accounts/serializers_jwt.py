from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Ajoute le rôle applicatif au payload JWT (non sensible, usage UI / API)."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = getattr(user, "role", "")
        token["email"] = getattr(user, "email", "")
        return token
