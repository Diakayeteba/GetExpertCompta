from django.contrib import admin

from .models import Invoice, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "billing_period", "amount_cents", "currency", "is_active")
    list_filter = ("billing_period", "is_active")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("business", "plan", "status", "started_at", "current_period_end")
    list_filter = ("status", "plan")
    search_fields = ("business__company_name", "external_reference")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("subscription", "issued_at", "amount_cents", "currency")
