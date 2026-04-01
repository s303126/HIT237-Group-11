from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class ThreatStatus(models.Model):
    code = models.CharField(max_length=10, unique=True)
    label = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return self.label[:25]

    def is_critical(self):
        """Returns True if this is the highest threat level."""
        return self.code == 'CR'

    @classmethod
    def get_threatened(cls):
        """Returns all statuses considered actively threatened."""
        return cls.objects.exclude(code__in=['LC', 'DD'])

class FaunaGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='icon/')
    
    def __str__(self):
        return self.name[:25]
    
    def get_species_count(self):
        """Returns total number of species in this group."""
        return self.species_set.count()

    def get_threatened_species(self):
        """Returns species in this group that have a threat status assigned."""
        return self.species_set.filter(threat_status__isnull=False)

    def get_recent_recordings(self, days=30):
        """Returns recordings for any species in this group within the last N days."""
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return Recording.objects.filter(
            species__fauna_group=self,
            date_recorded__gte=cutoff
        )

class Species(models.Model):
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, unique=True)
    fauna_group = models.ForeignKey(FaunaGroup, on_delete=models.PROTECT)
    threat_status = models.ForeignKey(ThreatStatus, null=True, blank=True, on_delete=models.SET_NULL)
    is_native = models.BooleanField(default=False)
    is_introduced = models.BooleanField(default=False)
    description = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return self.common_name[:25]
    
    def is_threatened(self):
        """Returns True if this species has a threat status assigned."""
        return self.threat_status is not None

    def get_recording_count(self):
        """Returns total number of recordings logged for this species."""
        return self.recording_set.count()

    def get_average_confidence(self):
        """Returns the mean confidence score across all recordings."""
        from django.db.models import Avg
        result = self.recording_set.aggregate(Avg('confidence_score'))
        return result['confidence_score__avg']

    def get_recent_recordings(self, days=30):
        """Returns recordings for this species within the last N days."""
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.recording_set.filter(date_recorded__gte=cutoff)

    def get_flagged_recordings(self):
        """Returns all recordings for this species flagged as anomalies."""
        return self.recording_set.filter(is_anomaly=True)

class User(AbstractUser):
    ROLE_TYPES = [
        ('researcher', 'Researcher'), 
        ('citizen_scientist', 'Citizen Scientist')
    ]
    role = models.CharField(max_length=20, default='citizen_scientist', choices=ROLE_TYPES)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_researcher(self):
        """Returns True if the user has the researcher role."""
        return self.role == 'researcher'

    def get_submission_count(self):
        """Returns total number of recordings this user has submitted."""
        return self.recording_set.count()

    def get_recent_submissions(self, days=30):
        """Returns recordings this user submitted in the last N days."""
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.recording_set.filter(date_submitted__gte=cutoff)

    def get_flagged_submissions(self):
        """Returns this user's recordings that have been flagged as anomalies."""
        return self.recording_set.filter(is_anomaly=True)

class Recording(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.PROTECT)
    audio_file = models.FileField(upload_to='recordings/')
    date_recorded = models.DateTimeField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_name = models.CharField(max_length=100, blank=True)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2)  # 0.00–1.00
    notes = models.TextField(blank=True)
    is_anomaly = models.BooleanField(default=False)
    anomaly_flag_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.species} — {self.date_recorded:%Y-%m-%d} by {self.user}"
    
    def flag(self, reason=''):
        """Flags this recording as an anomaly and saves."""
        self.is_anomaly = True
        self.anomaly_flag_reason = reason
        self.save()

    def unflag(self):
        """Clears the anomaly flag on this recording."""
        self.is_anomaly = False
        self.anomaly_flag_reason = ''
        self.save()

    def is_low_confidence(self, threshold=0.4):
        """Returns True if the confidence score is below the given threshold."""
        return self.confidence_score < threshold

    def get_anomalies(self):
        """Returns all Anomaly reports linked to this recording."""
        return self.anomaly_set.all()

    def has_unresolved_anomalies(self):
        """Returns True if any linked Anomaly records are unresolved."""
        return self.anomaly_set.filter(resolved=False).exists()

    @classmethod
    def get_timeline(cls, days=30):
        """Returns recent recordings ordered newest-first for the timeline view."""
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return cls.objects.filter(
            date_recorded__gte=cutoff
        ).select_related('species', 'user').order_by('-date_recorded')

    @classmethod
    def get_flagged(cls):
        """Returns all flagged recordings with related data prefetched."""
        return cls.objects.filter(
            is_anomaly=True
        ).select_related('species', 'user')
    
class Anomaly(models.Model):
    REASON_CHOICES = [
        ('wrong_species', 'Wrong Species'),
        ('poor_quality',  'Poor Audio Quality'),
        ('duplicate',     'Duplicate Entry'),
        ('location_error','Location Error'),
        ('other',         'Other'),
    ]
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE)
    flagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='flagged_anomalies')
    flagged_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_anomalies')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Anomaly on Recording #{self.recording_id} — {self.reason}"
    
    def is_pending(self):
        """Returns True if this anomaly has not been resolved."""
        return not self.resolved

    def resolve(self, user):
        """Marks this anomaly as resolved by the given user."""
        from django.utils import timezone
        self.resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()

    @classmethod
    def get_unresolved(cls):
        """Returns all unresolved anomalies, newest first."""
        return cls.objects.filter(
            resolved=False
        ).select_related('recording', 'flagged_by').order_by('-flagged_at')

    @classmethod
    def get_for_species(cls, species):
        """Returns all anomalies linked to recordings of a given species."""
        return cls.objects.filter(
            recording__species=species
        ).select_related('recording', 'flagged_by')
    
    
