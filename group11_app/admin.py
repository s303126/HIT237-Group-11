from django.contrib import admin
from .models import User, Species, FaunaGroup, ThreatStatus, Recording, Anomaly

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('username',)
    list_editable = ('is_approved',)
    fields = ('username', 'role', 'is_approved')
    actions = ['approve_researchers']

    def approve_researchers(self, request, queryset):
        updated = queryset.filter(role='researcher').update(is_approved=True)
        self.message_user(request, f"{updated} researcher(s) approved.")
    approve_researchers.short_description = "Approve selected researchers"

@admin.register(ThreatStatus)
class ThreatStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'label', 'description')

@admin.register(FaunaGroup)
class FaunaGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'fauna_group', 'threat_status', 'is_native', 'is_introduced')
    list_filter = ('fauna_group', 'threat_status', 'is_native', 'is_introduced')
    search_fields = ('common_name', 'scientific_name')

@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ('species', 'user', 'role', 'date_recorded', 'location_name', 'confidence_score')
    list_filter = ('species__fauna_group', 'role')
    search_fields = ('species__common_name', 'user__username', 'location_name')

@admin.register(Anomaly)
class AnomalyAdmin(admin.ModelAdmin):
    list_display = ('recording', 'reason', 'flagged_by', 'flagged_at', 'resolved', 'resolved_by', 'resolved_at')
    list_filter = ('resolved', 'reason')
    search_fields = ('recording__species__common_name', 'flagged_by__username')
    readonly_fields = ('flagged_at', 'resolved_at')