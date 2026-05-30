from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from group11_app.models import Recording, ThreatStatus

from .helpers import (
    create_anomaly,
    create_approved_researcher,
    create_citizen,
    create_recording,
    create_rejected_recording,
    create_species,
    create_threat_status,
    create_under_review_recording,
    create_unapproved_researcher,
)


class UserModelTests(TestCase):
    def test_is_researcher_returns_true_for_researcher_role(self):
        user = create_unapproved_researcher()

        self.assertTrue(user.is_researcher())

    def test_is_researcher_returns_false_for_citizen_scientist(self):
        user = create_citizen()

        self.assertFalse(user.is_researcher())

    def test_has_researcher_access_requires_researcher_role_and_approval(self):
        approved_researcher = create_approved_researcher()
        unapproved_researcher = create_unapproved_researcher()
        citizen = create_citizen()

        self.assertTrue(approved_researcher.has_researcher_access())
        self.assertFalse(unapproved_researcher.has_researcher_access())
        self.assertFalse(citizen.has_researcher_access())

    def test_get_pending_review_count_returns_under_review_total(self):
        user = create_approved_researcher()

        create_under_review_recording()
        create_under_review_recording()
        create_recording(status="approved")
        create_rejected_recording()

        self.assertEqual(user.get_pending_review_count(), 2)


class ThreatStatusModelTests(TestCase):
    def test_string_representation_returns_label(self):
        status = create_threat_status(code="VU", label="Vulnerable")

        self.assertEqual(str(status), "Vulnerable")

    def test_is_critical_returns_true_only_for_cr_code(self):
        critical = create_threat_status(code="CR", label="Critically Endangered")
        endangered = create_threat_status(code="EN", label="Endangered")

        self.assertTrue(critical.is_critical())
        self.assertFalse(endangered.is_critical())

    def test_get_threatened_excludes_least_concern_and_data_deficient(self):
        endangered = create_threat_status(code="EN", label="Endangered")
        least_concern = create_threat_status(code="LC", label="Least Concern")
        data_deficient = create_threat_status(code="DD", label="Data Deficient")

        threatened = ThreatStatus.get_threatened()

        self.assertIn(endangered, threatened)
        self.assertNotIn(least_concern, threatened)
        self.assertNotIn(data_deficient, threatened)


class SpeciesModelTests(TestCase):
    def test_species_is_threatened_when_threat_status_exists(self):
        status = create_threat_status(code="EN", label="Endangered")
        species = create_species(threat_status=status)

        self.assertTrue(species.is_threatened())

    def test_species_is_not_threatened_without_threat_status(self):
        species = create_species(threat_status=None)

        self.assertFalse(species.is_threatened())

    def test_get_recording_count_returns_number_of_linked_recordings(self):
        species = create_species()

        create_recording(species=species)
        create_recording(species=species)

        self.assertEqual(species.get_recording_count(), 2)

    def test_get_average_confidence_returns_mean_confidence_score(self):
        species = create_species()

        create_recording(species=species, confidence_score=Decimal("0.60"))
        create_recording(species=species, confidence_score=Decimal("0.80"))

        average = species.get_average_confidence()

        self.assertAlmostEqual(float(average), 0.70, places=2)

    def test_get_flagged_recordings_returns_recordings_with_anomalies(self):
        species = create_species()
        flagged_recording = create_recording(species=species)
        unflagged_recording = create_recording(species=species)

        create_anomaly(recording=flagged_recording)

        flagged_recordings = species.get_flagged_recordings()

        self.assertIn(flagged_recording, flagged_recordings)
        self.assertNotIn(unflagged_recording, flagged_recordings)


class RecordingModelTests(TestCase):
    def test_approved_recording_appears_in_timeline(self):
        approved = create_recording(status="approved")
        create_under_review_recording()
        create_rejected_recording()

        timeline = Recording.objects.get_timeline()

        self.assertIn(approved, timeline)

        for recording in timeline:
            self.assertEqual(recording.status, "approved")

    def test_under_review_recording_does_not_appear_in_timeline(self):
        recording = create_under_review_recording()

        timeline = Recording.objects.get_timeline()

        self.assertNotIn(recording, timeline)

    def test_rejected_recording_does_not_appear_in_timeline(self):
        recording = create_rejected_recording()

        timeline = Recording.objects.get_timeline()

        self.assertNotIn(recording, timeline)

    def test_approve_sets_status_and_timestamp(self):
        recording = create_under_review_recording()

        recording.approve()
        recording.refresh_from_db()

        self.assertEqual(recording.status, "approved")
        self.assertIsNotNone(recording.approved_at)

    def test_reject_sets_status_to_rejected(self):
        recording = create_under_review_recording()

        recording.reject()
        recording.refresh_from_db()

        self.assertEqual(recording.status, "rejected")

    def test_is_low_confidence_uses_decimal_threshold(self):
        low_confidence = create_recording(confidence_score=Decimal("0.30"))
        high_confidence = create_recording(confidence_score=Decimal("0.80"))

        self.assertTrue(low_confidence.is_low_confidence())
        self.assertFalse(high_confidence.is_low_confidence())

    def test_has_unresolved_anomalies_returns_true_when_unresolved_exists(self):
        recording = create_recording()
        create_anomaly(recording=recording, resolved=False)

        self.assertTrue(recording.has_unresolved_anomalies())

    def test_has_unresolved_anomalies_returns_false_when_only_resolved_exists(self):
        recording = create_recording()
        researcher = create_approved_researcher()
        create_anomaly(recording=recording, resolved=True, resolved_by=researcher)

        self.assertFalse(recording.has_unresolved_anomalies())


class AnomalyModelTests(TestCase):
    def test_anomaly_is_pending_when_not_resolved(self):
        anomaly = create_anomaly(resolved=False)

        self.assertTrue(anomaly.is_pending())

    def test_anomaly_is_not_pending_when_resolved(self):
        researcher = create_approved_researcher()
        anomaly = create_anomaly(resolved=True, resolved_by=researcher)

        self.assertFalse(anomaly.is_pending())

    def test_resolve_updates_resolution_fields(self):
        researcher = create_approved_researcher()
        anomaly = create_anomaly(resolved=False)

        anomaly.resolve(researcher)
        anomaly.refresh_from_db()

        self.assertTrue(anomaly.resolved)
        self.assertEqual(anomaly.resolved_by, researcher)
        self.assertIsNotNone(anomaly.resolved_at)