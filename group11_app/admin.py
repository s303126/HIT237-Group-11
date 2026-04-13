from django.contrib import admin
from .models import ThreatStatus, FaunaGroup, Species, User, Recording, Anomaly

admin.site.register(ThreatStatus)
admin.site.register(FaunaGroup)
admin.site.register(Species)
admin.site.register(User)
admin.site.register(Recording)
admin.site.register(Anomaly)