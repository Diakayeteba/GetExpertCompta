from django.contrib import admin

from .models import PaymentTransaction, PaymentWebhookLog


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("provider", "status", "amount_cents", "currency", "user", "created_at")
    list_filter = ("provider", "status")
    search_fields = ("external_id", "idempotency_key", "user__email")


@admin.register(PaymentWebhookLog)
class PaymentWebhookLogAdmin(admin.ModelAdmin):
    list_display = ("provider", "signature_valid", "processed", "received_at")
    list_filter = ("provider", "processed", "signature_valid")
