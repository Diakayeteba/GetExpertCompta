from django.contrib import admin

from .models import ExpertDocument, ExpertProfile, Specialty


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class ExpertDocumentInline(admin.TabularInline):
    model = ExpertDocument
    extra = 0


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "country", "city", "verification_status", "availability", "average_rating")
    list_filter = ("verification_status", "availability", "country")
    search_fields = ("user__email", "title", "city")
    filter_horizontal = ("specialties",)
    inlines = [ExpertDocumentInline]
