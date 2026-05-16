from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "actor", "object_type", "object_id", "ip_address")
    list_filter = ("action",)
    search_fields = ("object_repr", "actor__email")
    readonly_fields = (
        "created_at",
        "actor",
        "action",
        "object_type",
        "object_id",
        "object_repr",
        "metadata",
        "ip_address",
        "user_agent",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
