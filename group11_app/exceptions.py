class DuplicateRecording(Exception):
    """Raised when a duplicate record is submitted."""
    pass
class DuplicateAnomaly(Exception):
    """Raised when a duplicate anomaly is flagged."""
    pass
class InvalidAudioFileLength(Exception):
    """Raised when an audio file exceeds the maximum allowed duration."""
    pass
class AnomalyAlreadyResolved(Exception):
    """Raised when attempting to resolve an anomaly that is already resolved."""
    pass