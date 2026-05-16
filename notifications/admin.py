from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "channel", "read_at", "created_at")
    list_filter = ("event_type", "channel")
