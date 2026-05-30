from django.utils import timezone

from .models import Recording, Anomaly, Species
from .exceptions import DuplicateRecording, DuplicateAnomaly, InvalidAudioFileLength, AnomalyAlreadyResolved
from mutagen.mp3 import MP3


def validate_recording_duplicate(species, date_recorded, location_name, latitude, longitude, exclude_id=None):
    """
    Validates that a recording is not a duplicate based on core fields.
    
    Args:
        species: Species ForeignKey object
        date_recorded: DateTimeField value
        location_name: CharField value
        latitude: DecimalField value
        longitude: DecimalField value
        exclude_id: ID to exclude (for updates)
    
    Raises:
        DuplicateRecording: If a matching recording already exists
    """
    try:
        query = Recording.objects.filter(
            species=species,
            date_recorded=date_recorded,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
        )
        
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        if query.exists():
            raise DuplicateRecording("A recording with this species, date, and location already exists.")
    
    except Recording.DoesNotExist:
        pass


def validate_anomaly_duplicate(recording, reason):
    """
    Validates that an unresolved anomaly with this reason doesn't already exist on this recording.
    
    Args:
        recording: Recording instance
        reason: Reason choice string (e.g., 'wrong_species')
    
    Raises:
        DuplicateAnomaly: If an unresolved anomaly with the same reason already exists
    """
    try:
        query = Anomaly.objects.filter(
            recording=recording,
            reason=reason,
            resolved=False,  # Only check unresolved anomalies
        )
        
        if query.exists():
            raise DuplicateAnomaly(f"This recording already has an unresolved '{reason}' anomaly report.")
    
    except Anomaly.DoesNotExist:
        pass


def validate_audio_file(audio_file, max_seconds=60):
    """
    Validates that audio file is within max duration.
    
    Args:
        audio_file: Django UploadedFile object
        max_seconds: Maximum allowed duration in seconds (default 60)
    
    Raises:
        InvalidAudioFile: If audio file is too long or cannot be processed
    """
    try:
        audio = MP3(audio_file)
        duration = audio.info.length
        
        if duration > max_seconds:
            raise InvalidAudioFileLength(f"Audio file is too long ({duration:.1f}s). Maximum is {max_seconds} seconds.")
    
    except InvalidAudioFileLength:
        raise
    except Exception:
        pass


def validate_anomaly_not_resolved(anomaly):
    """
    Validates that an anomaly hasn't already been resolved.
    
    Args:
        anomaly: Anomaly instance
    
    Raises:
        AnomalyAlreadyResolved: If the anomaly is already resolved
    """
    try:
        if anomaly.resolved:
            raise AnomalyAlreadyResolved("This anomaly has already been resolved.")
    
    except Anomaly.DoesNotExist:
        pass
    
#Service Layer Architecture
def create_recording(user, species, date_recorded, location_name, latitude, longitude,
                     confidence_score, audio_file, notes=""):
    """
    Creates and persists a new Recording, running all validation first.
 
    Auto-approves the recording when the submitting user is an approved researcher.
 
    Args:
        user: User instance (the submitter)
        species: Species instance
        date_recorded: datetime
        location_name: str
        latitude: Decimal
        longitude: Decimal
        confidence_score: Decimal
        audio_file: UploadedFile
        notes: str (optional)
 
    Raises:
        DuplicateRecording: if an identical recording already exists
        InvalidAudioFileLength: if the audio file exceeds the 60-second limit
 
    Returns:
        Recording: the newly created instance
    """
    validate_recording_duplicate(species, date_recorded, location_name, latitude, longitude)
    validate_audio_file(audio_file)
 
    status = "approved" if user.has_researcher_access() else "under_review"
    approved_at = timezone.now() if status == "approved" else None
 
    recording = Recording.objects.create(
        user=user,
        species=species,
        date_recorded=date_recorded,
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        confidence_score=confidence_score,
        audio_file=audio_file,
        notes=notes,
        status=status,
        approved_at=approved_at,
    )
    return recording


def update_recording(recording, species, date_recorded, location_name, latitude, longitude,
                     confidence_score, audio_file, notes=""):
    """
    Validates and updates an existing Recording.
 
    Args:
        recording: Recording instance to update
        (remaining args mirror create_recording, excluding user)
 
    Raises:
        DuplicateRecording: if the new field values clash with another recording
 
    Returns:
        Recording: the updated instance
    """
    validate_recording_duplicate(
        species, date_recorded, location_name, latitude, longitude,
        exclude_id=recording.pk,
    )
 
    recording.species = species
    recording.date_recorded = date_recorded
    recording.location_name = location_name
    recording.latitude = latitude
    recording.longitude = longitude
    recording.confidence_score = confidence_score
    recording.audio_file = audio_file
    recording.notes = notes
    recording.save()
    return recording


def approve_recording(recording):
    """
    Approves a Recording and stamps the approval timestamp.
 
    Args:
        recording: Recording instance
 
    Returns:
        Recording: the updated instance
    """
    recording.approve()
    return recording


def reject_recording(recording):
    """
    Rejects a Recording.
 
    Args:
        recording: Recording instance
 
    Returns:
        Recording: the updated instance
    """
    recording.reject()
    return recording


def restore_recording(recording):
    """
    Restores a previously rejected Recording by re-approving it.
 
    Args:
        recording: Recording instance (must have status='rejected')
 
    Returns:
        Recording: the updated instance
    """
    recording.approve()
    return recording


def flag_anomaly(recording, flagged_by, reason):
    """
    Creates a new Anomaly flag on a Recording after validating for duplicates.
 
    Args:
        recording: Recording instance being flagged
        flagged_by: User instance raising the flag
        reason: str — one of Anomaly.REASON_CHOICES keys
 
    Raises:
        DuplicateAnomaly: if an unresolved anomaly with the same reason already exists
 
    Returns:
        Anomaly: the newly created instance
    """
    validate_anomaly_duplicate(recording=recording, reason=reason)
 
    anomaly = Anomaly.objects.create(
        recording=recording,
        flagged_by=flagged_by,
        reason=reason,
    )
    return anomaly


def resolve_anomaly(anomaly, resolved_by):
    """
    Resolves an Anomaly, recording which User performed the resolution.
 
    Args:
        anomaly: Anomaly instance to resolve
        resolved_by: User instance performing the resolution
 
    Raises:
        AnomalyAlreadyResolved: if the anomaly is already resolved
 
    Returns:
        Anomaly: the updated instance
    """
    validate_anomaly_not_resolved(anomaly)
    anomaly.resolve(resolved_by)
    return anomaly


def get_homepage_context():
    """
    Aggregates data needed for the homepage from Recording and Species.
 
    Returns:
        dict with keys:
            recent_recordings  — latest 3 approved recordings
    """
    return {
        "recent_recordings": Recording.objects.get_timeline()[:3],
    }


def get_species_detail_context(species):
    """
    Aggregates Recording data for a Species detail page.
 
    Args:
        species: Species instance
 
    Returns:
        dict with keys:
            recent_recordings  — recordings in the last 30 days for this species
            flagged_recordings — recordings with at least one anomaly flag
    """
    return {
        "recent_recordings": species.get_recent_recordings(),
        "flagged_recordings": species.get_flagged_recordings(),
    }


def get_anomaly_list_context():
    """
    Aggregates unresolved Anomaly records and high-flag User data for the
    anomaly list page.
 
    Returns:
        dict with keys:
            anomalies     — unresolved Anomaly queryset
            flagged_users — users with 3+ flagged recordings
    """
    return {
        "anomalies": Anomaly.objects.get_unresolved(),
        "flagged_users": Recording.objects.get_users_with_high_flags(),
    }


def get_review_queue_context(status_filter="under_review"):
    """
    Aggregates Recording data for the researcher review queue, filtered by status.
 
    Args:
        status_filter: str — 'under_review' | 'approved' | 'rejected'
 
    Returns:
        dict with keys:
            recordings      — filtered Recording queryset
            rejected_users  — users with 3+ rejected recordings
            current_filter  — the active status_filter string
    """
    if status_filter == "approved":
        recordings = Recording.objects.get_recently_approved()
    elif status_filter == "rejected":
        recordings = Recording.objects.get_rejected()
    else:
        recordings = Recording.objects.get_pending_review()
 
    return {
        "recordings": recordings,
        "rejected_users": Recording.objects.get_users_with_high_rejections(),
        "current_filter": status_filter,
    }
