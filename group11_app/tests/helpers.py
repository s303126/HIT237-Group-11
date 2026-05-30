from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from group11_app.models import (
    Anomaly,
    FaunaGroup,
    Recording,
    Species,
    ThreatStatus,
)

User = get_user_model()


def create_user(
    username="testuser",
    password="testpass123",
    role="citizen_scientist",
    is_approved=False,
):
    """
    Creates a user for tests.

    role:
        - "citizen_scientist"
        - "researcher"

    is_approved:
        Used for researcher accounts. A researcher only has researcher access
        if role="researcher" and is_approved=True.
    """
    return User.objects.create_user(
        username=username,
        password=password,
        role=role,
        is_approved=is_approved,
    )


def create_citizen(username="citizen"):
    return create_user(
        username=username,
        role="citizen_scientist",
        is_approved=False,
    )


def create_unapproved_researcher(username="unapproved_researcher"):
    return create_user(
        username=username,
        role="researcher",
        is_approved=False,
    )


def create_approved_researcher(username="approved_researcher"):
    return create_user(
        username=username,
        role="researcher",
        is_approved=True,
    )


def create_threat_status(
    code="EN",
    label="Endangered",
    description="At risk of extinction.",
):
    return ThreatStatus.objects.create(
        code=code,
        label=label,
        description=description,
    )


def create_fauna_group(name="Birds"):
    """
    Creates a fauna group.

    Note:
    The model currently has an ImageField for icon. Django does not require
    a file to be physically uploaded here unless extra validation is added,
    so this can stay as a simple string path for tests.
    """
    return FaunaGroup.objects.create(
        name=name,
        icon="icon/test-icon.png",
    )


def create_species(
    common_name="Bush Stone-curlew",
    scientific_name="Burhinus grallarius",
    fauna_group=None,
    threat_status=None,
    is_native=True,
    is_introduced=False,
):
    if fauna_group is None:
        fauna_group = create_fauna_group()

    return Species.objects.create(
        common_name=common_name,
        scientific_name=scientific_name,
        fauna_group=fauna_group,
        threat_status=threat_status,
        is_native=is_native,
        is_introduced=is_introduced,
        description="Test species description.",
    )


def create_fake_mp3_file(filename="test.mp3"):
    """
    Creates a small fake MP3 upload object.

    This is enough for tests that do not inspect real audio duration.
    The service layer currently uses mutagen.MP3 for duration checks, so tests
    that call create_recording() should usually mock validate_audio_file().
    """
    return SimpleUploadedFile(
        filename,
        b"fake mp3 content",
        content_type="audio/mpeg",
    )


def create_recording(
    user=None,
    species=None,
    date_recorded=None,
    location_name="Darwin",
    latitude=Decimal("-12.463400"),
    longitude=Decimal("130.845600"),
    confidence_score=Decimal("0.80"),
    audio_file="recordings/test.mp3",
    notes="Test recording notes.",
    status="approved",
    approved_at=None,
):
    if user is None:
        user = create_citizen()

    if species is None:
        species = create_species()

    if date_recorded is None:
        date_recorded = timezone.now()

    if approved_at is None and status == "approved":
        approved_at = timezone.now()

    return Recording.objects.create(
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


def create_under_review_recording(user=None, species=None):
    if user is None:
        user = create_citizen()

    return create_recording(
        user=user,
        species=species,
        status="under_review",
        approved_at=None,
    )


def create_rejected_recording(user=None, species=None):
    if user is None:
        user = create_citizen()

    return create_recording(
        user=user,
        species=species,
        status="rejected",
        approved_at=None,
    )


def create_anomaly(
    recording=None,
    flagged_by=None,
    reason="poor_quality",
    resolved=False,
    resolved_by=None,
):
    if recording is None:
        recording = create_recording()

    if flagged_by is None:
        flagged_by = create_citizen(username="flagger")

    anomaly = Anomaly.objects.create(
        recording=recording,
        flagged_by=flagged_by,
        reason=reason,
        resolved=resolved,
        resolved_by=resolved_by,
    )

    if resolved:
        anomaly.resolved_at = timezone.now()
        anomaly.save()

    return anomaly