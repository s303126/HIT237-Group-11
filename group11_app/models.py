from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.utils import timezone 

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
    
class FaunaGroupManager(models.Manager):
    def get_with_species_counts(self):
        # Returns all fauna groups annotated with their total number of species
        return self.annotate(species_count=Count('species'))
    
    def get_with_recording_counts(self):
        # Returns all fauna groups annotated with their total number of recordings
        return (self.annotate(recording_count=Count('species__recording'))
                    .order_by('-recording_count'))

class FaunaGroup(models.Model):
    objects = FaunaGroupManager()
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
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return Recording.objects.filter(
            species__fauna_group=self,
            date_recorded__gte=cutoff
        )
    
class SpeciesManager(models.Manager):
    def get_threatened(self):
        # Returns all threatened species with related threat status and fauna group
        return (self.filter(threat_status__isnull=False)
                .select_related('threat_status', 'fauna_group'))
    
    def get_native(self):
        # Returns all native species
        return (self.filter(is_native=True)
                .select_related('fauna_group'))
    
    def get_with_recording_counts(self):
        # Returns all species annotated with their total number of recordings
        return (self.annotate(recording_count=Count('recording'))
                .select_related('threat_status', 'fauna_group')
                .order_by('-recording_count'))
    
    def search_by_name(self, query):
        # Returns species matching a common or scientific name search
        return (self.filter(common_name__icontains=query) |
                self.filter(scientific_name__icontains=query))

class Species(models.Model):
    objects = SpeciesManager()
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
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.recording_set.filter(date_recorded__gte=cutoff)

    def get_flagged_recordings(self):
        """Returns all recordings for this species flagged as anomalies."""
        return self.recording_set.filter(is_anomaly=True)

class User(User):
    ROLE_TYPES = [
        ('researcher', 'Researcher'), 
        ('citizen_scientist', 'Citizen Scientist')
    ]
    role = models.CharField(max_length=20, default='citizen_scientist', choices=ROLE_TYPES)
    user_group = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True
    )
    user_permission = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True
    )
    
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
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.recording_set.filter(date_submitted__gte=cutoff)

    def get_flagged_submissions(self):
        """Returns this user's recordings that have been flagged as anomalies."""
        return self.recording_set.filter(is_anomaly=True)
    
class RecordingManager(models.Manager):
    def get_timeline(self):
        # Returns all recordings ordered newest first, with related
        #species, user and anomalies pre-fetched to avoid extra database queries
        return (self.select_related('species', 'user')
                .prefetch_related('anomaly_set')
                .order_by('-date_recorded'))
    
    def get_recent(self, days=7):
        # Returns all recordings submitted within the last 7 days
        # 'days' parameter can be adjusted as needed
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return (self.select_related('species', 'user')
                .filter(date_recorded__gte=cutoff)
                .order_by('-date_recorded'))
    
    def get_by_species(self, species):
        # Returns all recordings for a given species, ordered newest to oldest
        return (self.filter(species=species)
               .select_related('user')
               .order_by('-date_recorded'))
    
    def get_by_user(self, user):
        # Returns all recordings from a specific user, ordered newest to oldest
        return (self.filter(user=user)
               .select_related('species')
               .order_by('-date_recorded'))
    
    def get_with_anomaly_count(self):
        # Returns all recordings with a count of anomalies (flags) for each recording
        return (self.annotate(anomaly_count=Count('anomaly'))
                .select_related('species', 'user')
                .order_by('-date_recorded'))
    
    def get_by_threatened_species(self):
        # Returns all recordings of threatened species only
        # Excludes LC (Least Concern) and DD (Data Deficient)
        # Chains across Recording to Species to ThreatStatus
        return (self.filter(species__threat_status__isnull=False)
                .exclude(species__threat_status__code__in=['LC', 'DD'])
                .select_related('species__threat_status', 'user')
                .order_by('-date_recorded'))
    
    def get_statistics(self):
        # Returns total number of recordings and average confidence score
        return self.aggregate(
                total_recordings=Count('id'),
                avg_confidence=Avg('confidence_score'))
    
    def get_top_locations(self, limit=3, threatened_only=False):
        # Returns the top 3 locations with the most recordings
        # threatened_only parameter filters to only show threatened species top locations
        qs = self.annotate(recording_count=Count('id'))
        if threatened_only:
            qs = qs.filter(species__threat_status__isnull=False)
        return qs.order_by('-recording_count')[:limit]

    def get_users_with_high_flags(self):
        # Returns users who have had 3 or more recordings flagged
        from django.db.models import Count
        return (self.values('user__username')
                .annotate(flagged_count=Count('anomaly'))
                .filter(flagged_count__gte=3)
                .order_by('-flagged_count'))

class Recording(models.Model):
    objects = RecordingManager()
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
    def get_flagged(cls):
        """Returns all flagged recordings with related data prefetched."""
        return cls.objects.filter(
            is_anomaly=True
        ).select_related('species', 'user')
    

class AnomalyManager(models.Manager):
    def get_unresolved(self):
        # Returns all unresolved anomalies, newest first
        return (self.filter(resolved=False)
                .select_related('recording', 'flagged_by')
                .order_by('-flagged_at'))
    
    def get_by_reason(self, reason):
        # Returns all anomalies filtered by reason type
        return (self.filter(reason=reason)
                .select_related('recording', 'flagged_by'))
    
    def get_for_species(self, species):
        # Returns all anomalies based on species
        return (self.filter(recording__species=species)
                .select_related('recording', 'flagged_by'))
    
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
        self.resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()
