from .models import Recording, Anomaly
from .exceptions import DuplicateRecording, DuplicateAnomaly


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