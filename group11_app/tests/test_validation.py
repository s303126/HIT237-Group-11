from decimal import Decimal
from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from group11_app.exceptions import (
    DuplicateAnomaly,
    DuplicateRecording,
    InvalidAudioFileLength,
)
from group11_app.models import Recording
from group11_app.services import (
    validate_anomaly_duplicate,
    validate_audio_file,
    validate_recording_duplicate,
)

from .helpers import (
    create_anomaly,
    create_approved_researcher,
    create_citizen,
    create_recording,
    create_species,
)


class RecordingModelValidationTests(TestCase):
    def setUp(self):
        self.user = create_citizen()
        self.species = create_species()

    def build_recording(self, confidence_score=Decimal("0.80"), audio_file="recordings/test.mp3"):
        return Recording(
            user=self.user,
            species=self.species,
            date_recorded=timezone.now(),
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
            confidence_score=confidence_score,
            audio_file=audio_file,
            notes="Validation test recording.",
            status="approved",
        )

    def test_valid_decimal_confidence_score_passes_model_validation(self):
        recording = self.build_recording(confidence_score=Decimal("0.80"))

        recording.full_clean()

    def test_confidence_score_rejects_too_many_total_digits(self):
        recording = self.build_recording(confidence_score=Decimal("123.45"))

        with self.assertRaises(ValidationError):
            recording.full_clean()

    def test_audio_file_accepts_mp3_extension(self):
        recording = self.build_recording(audio_file="recordings/test.mp3")

        recording.full_clean()

    def test_audio_file_rejects_non_mp3_extension(self):
        recording = self.build_recording(audio_file="recordings/test.wav")

        with self.assertRaises(ValidationError):
            recording.full_clean()


class RecordingDuplicateValidationTests(TestCase):
    def setUp(self):
        self.species = create_species()
        self.date_recorded = timezone.now()

    def test_duplicate_recording_same_species_date_and_location_is_rejected(self):
        create_recording(
            species=self.species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
        )

        with self.assertRaises(DuplicateRecording):
            validate_recording_duplicate(
                species=self.species,
                date_recorded=self.date_recorded,
                location_name="Darwin",
                latitude=Decimal("-12.463400"),
                longitude=Decimal("130.845600"),
            )

    def test_recording_duplicate_validation_allows_different_species(self):
        existing_species = create_species(
            common_name="Northern Quoll",
            scientific_name="Dasyurus hallucatus",
        )
        different_species = create_species(
            common_name="Gouldian Finch",
            scientific_name="Chloebia gouldiae",
        )

        create_recording(
            species=existing_species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
        )

        try:
            validate_recording_duplicate(
                species=different_species,
                date_recorded=self.date_recorded,
                location_name="Darwin",
                latitude=Decimal("-12.463400"),
                longitude=Decimal("130.845600"),
            )
        except DuplicateRecording:
            self.fail("Different species should not be treated as a duplicate recording.")

    def test_recording_duplicate_validation_allows_different_location(self):
        create_recording(
            species=self.species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
        )

        try:
            validate_recording_duplicate(
                species=self.species,
                date_recorded=self.date_recorded,
                location_name="Palmerston",
                latitude=Decimal("-12.480000"),
                longitude=Decimal("130.980000"),
            )
        except DuplicateRecording:
            self.fail("Different location should not be treated as a duplicate recording.")

    def test_recording_duplicate_validation_excludes_current_recording_on_update(self):
        recording = create_recording(
            species=self.species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
        )

        try:
            validate_recording_duplicate(
                species=self.species,
                date_recorded=self.date_recorded,
                location_name="Darwin",
                latitude=Decimal("-12.463400"),
                longitude=Decimal("130.845600"),
                exclude_id=recording.pk,
            )
        except DuplicateRecording:
            self.fail("A recording should not be considered a duplicate of itself during update.")


class AudioValidationTests(TestCase):
    @patch("group11_app.services.MP3")
    def test_audio_file_under_max_length_passes(self, mock_mp3):
        audio = Mock()
        audio.info.length = 30
        mock_mp3.return_value = audio

        try:
            validate_audio_file("recordings/test.mp3", max_seconds=60)
        except InvalidAudioFileLength:
            self.fail("Audio under the maximum duration should pass validation.")

    @patch("group11_app.services.MP3")
    def test_audio_file_over_max_length_raises_exception(self, mock_mp3):
        audio = Mock()
        audio.info.length = 90
        mock_mp3.return_value = audio

        with self.assertRaises(InvalidAudioFileLength):
            validate_audio_file("recordings/test.mp3", max_seconds=60)

    @patch("group11_app.services.MP3")
    def test_unreadable_audio_file_is_ignored_by_current_validation_design(self, mock_mp3):
        mock_mp3.side_effect = Exception("Unreadable fake audio file.")

        try:
            validate_audio_file("recordings/broken.mp3", max_seconds=60)
        except Exception:
            self.fail("Current validation design swallows unreadable audio exceptions.")


class AnomalyDuplicateValidationTests(TestCase):
    def setUp(self):
        self.flagger = create_citizen(username="flagger")
        self.researcher = create_approved_researcher(username="researcher")
        self.recording = create_recording(user=self.flagger)

    def test_unresolved_duplicate_anomaly_same_reason_is_rejected(self):
        create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=False,
        )

        with self.assertRaises(DuplicateAnomaly):
            validate_anomaly_duplicate(
                recording=self.recording,
                reason="poor_quality",
            )

    def test_different_anomaly_reason_is_allowed(self):
        create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=False,
        )

        try:
            validate_anomaly_duplicate(
                recording=self.recording,
                reason="wrong_species",
            )
        except DuplicateAnomaly:
            self.fail("Different anomaly reasons should be allowed on the same recording.")

    def test_resolved_anomaly_does_not_block_new_same_reason_anomaly(self):
        create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=True,
            resolved_by=self.researcher,
        )

        try:
            validate_anomaly_duplicate(
                recording=self.recording,
                reason="poor_quality",
            )
        except DuplicateAnomaly:
            self.fail("Resolved anomalies should not block future anomaly reports.")