from django.contrib import admin

from .models import ServiceRequest, ServiceRequestAttachment, ServiceRequestExpert


class AttachmentInline(admin.TabularInline):
    model = ServiceRequestAttachment
    extra = 0


class ExpertInline(admin.TabularInline):
    model = ServiceRequestExpert
    extra = 0


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "business", "country", "status", "created_at")
    list_filter = ("status", "country")
    inlines = [AttachmentInline, ExpertInline]
