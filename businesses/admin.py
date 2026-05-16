from django.contrib import admin

from .models import BusinessProfile


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "country", "city")
    search_fields = ("company_name", "user__email")
