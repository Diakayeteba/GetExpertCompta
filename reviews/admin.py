from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("expert", "business", "rating", "moderation_status", "created_at")
    list_filter = ("moderation_status", "rating")
    search_fields = ("comment", "business__company_name", "expert__user__email")
