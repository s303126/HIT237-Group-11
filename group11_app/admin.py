from django.contrib import admin
from .models import User, Species, FaunaGroup, ThreatStatus, Recording, Anomaly

# Basic model registration
admin.site.register(User)
admin.site.register(Species)
admin.site.register(FaunaGroup)
admin.site.register(ThreatStatus)
admin.site.register(Recording)

# Custom Anomaly admin
@admin.register(Anomaly)
class AnomalyAdmin(admin.ModelAdmin):
    list_display = ('recording', 'reason', 'flagged_by', 'flagged_at', 'resolved', 'resolved_by', 'resolved_at')
    list_filter = ('resolved', 'reason')
    search_fields = ('recording__species__common_name', 'flagged_by__username')
    readonly_fields = ('flagged_at', 'resolved_at')
