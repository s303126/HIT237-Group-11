from django.contrib import admin
from .models import ThreatStatus, FaunaGroup, Species, User, Recording, Anomaly

@admin.register(ThreatStatus)
class ThreatStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "description")
    search_fields = ("code", "label")

@admin.register(FaunaGroup)
class FaunaGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "icon")
    search_fields = ("name",)

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("common_name", "scientific_name", "fauna_group", "threat_status", "is_native", "is_introduced")
    list_filter = ("fauna_group", "threat_status", "is_native", "is_introduced")
    search_fields = ("common_name", "scientific_name")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")

@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ("species", "user", "date_recorded", "date_submitted", "location_name", "confidence_score", "is_anomaly")
    list_filter = ("species", "date_recorded", "is_anomaly")
    search_fields = ("species__common_name", "location_name", "user__username")

@admin.register(Anomaly)
class AnomalyAdmin(admin.ModelAdmin):
    list_display = ("recording", "flagged_by", "flagged_at", "reason", "resolved")
    list_filter = ("reason", "resolved", "flagged_at")
    search_fields = ("recording__species__common_name", "flagged_by__username", "reason")