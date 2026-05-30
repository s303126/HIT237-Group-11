from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from group11_app.exceptions import (
    AnomalyAlreadyResolved,
    DuplicateAnomaly,
    DuplicateRecording,
)

from group11_app.models import Anomaly, Recording

from group11_app.services import (
    approve_recording,
    create_recording,
    flag_anomaly,
    get_anomaly_list_context,
    get_homepage_context,
    get_review_queue_context,
    get_species_detail_context,
    reject_recording,
    resolve_anomaly,
    restore_recording,
    validate_anomaly_duplicate,
    validate_anomaly_not_resolved,
    validate_recording_duplicate,
)

from .helpers import (
    create_anomaly,
    create_approved_researcher,
    create_citizen,
    create_fake_mp3_file,
    create_recording as create_recording_object,
    create_rejected_recording,
    create_species,
    create_under_review_recording,
    create_unapproved_researcher,
)


class RecordingCreationServiceTests(TestCase):
    def setUp(self):
        self.species = create_species()
        self.date_recorded = timezone.now()

    @patch("group11_app.services.validate_audio_file")
    def test_citizen_submission_is_created_under_review(self, mock_validate_audio):
        citizen = create_citizen()
        audio_file = create_fake_mp3_file()

        recording = create_recording(
            user=citizen,
            species=self.species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
            confidence_score=Decimal("0.80"),
            audio_file=audio_file,
            notes="Citizen submitted recording.",
        )

        self.assertEqual(recording.user, citizen)
        self.assertEqual(recording.status, "under_review")
        self.assertIsNone(recording.approved_at)
        mock_validate_audio.assert_called_once_with(audio_file)

    @patch("group11_app.services.validate_audio_file")
    def test_unapproved_researcher_submission_is_created_under_review(self, mock_validate_audio):
        researcher = create_unapproved_researcher()
        audio_file = create_fake_mp3_file()

        recording = create_recording(
            user=researcher,
            species=self.species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
            confidence_score=Decimal("0.80"),
            audio_file=audio_file,
            notes="Unapproved researcher submitted recording.",
        )

        self.assertEqual(recording.status, "under_review")
        self.assertIsNone(recording.approved_at)

    @patch("group11_app.services.validate_audio_file")
    def test_approved_researcher_submission_is_auto_approved(self, mock_validate_audio):
        researcher = create_approved_researcher()
        audio_file = create_fake_mp3_file()

        recording = create_recording(
            user=researcher,
            species=self.species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
            confidence_score=Decimal("0.80"),
            audio_file=audio_file,
            notes="Researcher submitted recording.",
        )

        self.assertEqual(recording.user, researcher)
        self.assertEqual(recording.status, "approved")
        self.assertIsNotNone(recording.approved_at)

    @patch("group11_app.services.validate_audio_file")
    def test_duplicate_recording_raises_duplicate_recording_exception(self, mock_validate_audio):
        citizen = create_citizen()
        audio_file = create_fake_mp3_file()

        create_recording_object(
            user=citizen,
            species=self.species,
            date_recorded=self.date_recorded,
            location_name="Darwin",
            latitude=Decimal("-12.463400"),
            longitude=Decimal("130.845600"),
            confidence_score=Decimal("0.80"),
            status="under_review",
        )

        with self.assertRaises(DuplicateRecording):
            create_recording(
                user=citizen,
                species=self.species,
                date_recorded=self.date_recorded,
                location_name="Darwin",
                latitude=Decimal("-12.463400"),
                longitude=Decimal("130.845600"),
                confidence_score=Decimal("0.80"),
                audio_file=audio_file,
                notes="Duplicate recording attempt.",
            )


class RecordingReviewServiceTests(TestCase):
    def test_approve_recording_changes_status_to_approved(self):
        recording = create_under_review_recording()

        updated_recording = approve_recording(recording)
        updated_recording.refresh_from_db()

        self.assertEqual(updated_recording.status, "approved")
        self.assertIsNotNone(updated_recording.approved_at)

    def test_reject_recording_changes_status_to_rejected(self):
        recording = create_under_review_recording()

        updated_recording = reject_recording(recording)
        updated_recording.refresh_from_db()

        self.assertEqual(updated_recording.status, "rejected")

    def test_restore_recording_reapproves_rejected_recording(self):
        recording = create_rejected_recording()

        updated_recording = restore_recording(recording)
        updated_recording.refresh_from_db()

        self.assertEqual(updated_recording.status, "approved")
        self.assertIsNotNone(updated_recording.approved_at)


class DuplicateValidationServiceTests(TestCase):
    def setUp(self):
        self.species = create_species()
        self.date_recorded = timezone.now()

    def test_validate_recording_duplicate_raises_for_existing_recording(self):
        create_recording_object(
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

    def test_validate_recording_duplicate_allows_different_location(self):
        create_recording_object(
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
            self.fail("validate_recording_duplicate incorrectly rejected a different location.")

    def test_validate_recording_duplicate_excludes_current_recording_on_update(self):
        recording = create_recording_object(
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
            self.fail("validate_recording_duplicate should ignore the recording being updated.")


class AnomalyServiceTests(TestCase):
    def setUp(self):
        self.recording = create_recording_object()
        self.flagger = create_citizen(username="flagger")
        self.researcher = create_approved_researcher()

    def test_flag_anomaly_creates_anomaly(self):
        anomaly = flag_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
        )

        self.assertEqual(anomaly.recording, self.recording)
        self.assertEqual(anomaly.flagged_by, self.flagger)
        self.assertEqual(anomaly.reason, "poor_quality")
        self.assertFalse(anomaly.resolved)

    def test_duplicate_unresolved_anomaly_same_reason_is_rejected(self):
        create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
        )

        with self.assertRaises(DuplicateAnomaly):
            validate_anomaly_duplicate(
                recording=self.recording,
                reason="poor_quality",
            )

    def test_same_recording_can_have_different_unresolved_anomaly_reason(self):
        create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
        )

        anomaly = flag_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="wrong_species",
        )

        self.assertEqual(anomaly.reason, "wrong_species")
        self.assertEqual(Anomaly.objects.filter(recording=self.recording).count(), 2)

    def test_resolve_anomaly_marks_anomaly_as_resolved(self):
        anomaly = create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
        )

        resolved_anomaly = resolve_anomaly(
            anomaly=anomaly,
            resolved_by=self.researcher,
        )
        resolved_anomaly.refresh_from_db()

        self.assertTrue(resolved_anomaly.resolved)
        self.assertEqual(resolved_anomaly.resolved_by, self.researcher)
        self.assertIsNotNone(resolved_anomaly.resolved_at)

    def test_resolving_already_resolved_anomaly_raises_exception(self):
        anomaly = create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=True,
            resolved_by=self.researcher,
        )

        with self.assertRaises(AnomalyAlreadyResolved):
            validate_anomaly_not_resolved(anomaly)


class ContextServiceTests(TestCase):
    def test_homepage_context_returns_three_recent_approved_recordings(self):
        for index in range(5):
            species = create_species(
                common_name=f"Species {index}",
                scientific_name=f"Species scientificus {index}",
            )
            create_recording_object(
                species=species,
                status="approved",
            )

        create_under_review_recording()

        context = get_homepage_context()

        self.assertIn("recent_recordings", context)
        self.assertEqual(len(context["recent_recordings"]), 3)

        for recording in context["recent_recordings"]:
            self.assertEqual(recording.status, "approved")

    def test_species_detail_context_contains_recent_and_flagged_recordings(self):
        species = create_species(
            common_name="Northern Quoll",
            scientific_name="Dasyurus hallucatus",
        )
        recording = create_recording_object(species=species)
        create_anomaly(recording=recording)

        context = get_species_detail_context(species)

        self.assertIn("recent_recordings", context)
        self.assertIn("flagged_recordings", context)
        self.assertIn(recording, context["flagged_recordings"])

    def test_anomaly_list_context_contains_unresolved_anomalies(self):
        unresolved_anomaly = create_anomaly(reason="poor_quality")
        resolved_anomaly = create_anomaly(reason="wrong_species", resolved=True)

        context = get_anomaly_list_context()

        self.assertIn("anomalies", context)
        self.assertIn(unresolved_anomaly, context["anomalies"])
        self.assertNotIn(resolved_anomaly, context["anomalies"])

    def test_review_queue_context_defaults_to_under_review_recordings(self):
        pending_recording = create_under_review_recording()
        create_rejected_recording()
        create_recording_object(status="approved")

        context = get_review_queue_context()

        self.assertEqual(context["current_filter"], "under_review")
        self.assertIn(pending_recording, context["recordings"])

        for recording in context["recordings"]:
            self.assertEqual(recording.status, "under_review")

    def test_review_queue_context_can_return_rejected_recordings(self):
        rejected_recording = create_rejected_recording()
        create_under_review_recording()
        create_recording_object(status="approved")

        context = get_review_queue_context(status_filter="rejected")

        self.assertEqual(context["current_filter"], "rejected")
        self.assertIn(rejected_recording, context["recordings"])

        for recording in context["recordings"]:
            self.assertEqual(recording.status, "rejected")

    def test_review_queue_context_can_return_recently_approved_recordings(self):
        approved_recording = create_recording_object(status="approved")
        create_under_review_recording()
        create_rejected_recording()

        context = get_review_queue_context(status_filter="approved")

        self.assertEqual(context["current_filter"], "approved")
        self.assertIn(approved_recording, context["recordings"])

        for recording in context["recordings"]:
            self.assertEqual(recording.status, "approved")