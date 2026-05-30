from django.test import TestCase
from django.urls import reverse

from group11_app.exceptions import AnomalyAlreadyResolved, DuplicateAnomaly
from group11_app.models import Anomaly
from group11_app.services import (
    flag_anomaly,
    resolve_anomaly,
    validate_anomaly_duplicate,
    validate_anomaly_not_resolved,
)

from .helpers import (
    create_anomaly,
    create_approved_researcher,
    create_citizen,
    create_recording,
    create_species,
)


class AnomalyManagerTests(TestCase):
    def test_get_unresolved_returns_only_unresolved_anomalies(self):
        unresolved = create_anomaly(resolved=False)
        resolved = create_anomaly(resolved=True, resolved_by=create_approved_researcher())

        anomalies = Anomaly.objects.get_unresolved()

        self.assertIn(unresolved, anomalies)
        self.assertNotIn(resolved, anomalies)

    def test_get_by_reason_filters_anomalies_by_reason(self):
        poor_quality = create_anomaly(reason="poor_quality")
        wrong_species = create_anomaly(reason="wrong_species")

        results = Anomaly.objects.get_by_reason("poor_quality")

        self.assertIn(poor_quality, results)
        self.assertNotIn(wrong_species, results)

    def test_get_for_species_returns_anomalies_for_selected_species(self):
        target_species = create_species(
            common_name="Northern Quoll",
            scientific_name="Dasyurus hallucatus",
        )
        other_species = create_species(
            common_name="Gouldian Finch",
            scientific_name="Chloebia gouldiae",
        )

        target_recording = create_recording(species=target_species)
        other_recording = create_recording(species=other_species)

        target_anomaly = create_anomaly(recording=target_recording)
        other_anomaly = create_anomaly(recording=other_recording)

        results = Anomaly.objects.get_for_species(target_species)

        self.assertIn(target_anomaly, results)
        self.assertNotIn(other_anomaly, results)

    def test_search_finds_unresolved_anomaly_by_species_common_name(self):
        species = create_species(
            common_name="Northern Quoll",
            scientific_name="Dasyurus hallucatus",
        )
        recording = create_recording(species=species)
        anomaly = create_anomaly(recording=recording)

        results = Anomaly.objects.search("Quoll")

        self.assertIn(anomaly, results)

    def test_search_finds_unresolved_anomaly_by_flagger_username(self):
        flagger = create_citizen(username="field_observer")
        recording = create_recording()
        anomaly = create_anomaly(recording=recording, flagged_by=flagger)

        results = Anomaly.objects.search("field_observer")

        self.assertIn(anomaly, results)

    def test_search_excludes_resolved_anomalies(self):
        flagger = create_citizen(username="resolved_user")
        researcher = create_approved_researcher()
        recording = create_recording()

        resolved_anomaly = create_anomaly(
            recording=recording,
            flagged_by=flagger,
            resolved=True,
            resolved_by=researcher,
        )

        results = Anomaly.objects.search("resolved_user")

        self.assertNotIn(resolved_anomaly, results)


class AnomalyServiceBehaviourTests(TestCase):
    def setUp(self):
        self.recording = create_recording()
        self.flagger = create_citizen(username="flagger")
        self.researcher = create_approved_researcher()

    def test_flag_anomaly_creates_unresolved_anomaly(self):
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
            resolved=False,
        )

        with self.assertRaises(DuplicateAnomaly):
            validate_anomaly_duplicate(
                recording=self.recording,
                reason="poor_quality",
            )

    def test_same_recording_can_have_different_anomaly_reasons(self):
        create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=False,
        )

        second_anomaly = flag_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="wrong_species",
        )

        self.assertEqual(second_anomaly.reason, "wrong_species")
        self.assertEqual(Anomaly.objects.filter(recording=self.recording).count(), 2)

    def test_resolved_anomaly_does_not_block_same_reason_later(self):
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
            self.fail("Resolved anomalies should not block a new anomaly with the same reason.")

    def test_resolve_anomaly_marks_anomaly_as_resolved(self):
        anomaly = create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=False,
        )

        resolved_anomaly = resolve_anomaly(
            anomaly=anomaly,
            resolved_by=self.researcher,
        )
        resolved_anomaly.refresh_from_db()

        self.assertTrue(resolved_anomaly.resolved)
        self.assertEqual(resolved_anomaly.resolved_by, self.researcher)
        self.assertIsNotNone(resolved_anomaly.resolved_at)

    def test_validate_anomaly_not_resolved_raises_for_resolved_anomaly(self):
        anomaly = create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=True,
            resolved_by=self.researcher,
        )

        with self.assertRaises(AnomalyAlreadyResolved):
            validate_anomaly_not_resolved(anomaly)


class AnomalyViewTests(TestCase):
    def setUp(self):
        self.flagger = create_citizen(username="flagger")
        self.other_citizen = create_citizen(username="other_citizen")
        self.researcher = create_approved_researcher()
        self.recording = create_recording(user=self.flagger)
        self.anomaly = create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
            reason="poor_quality",
            resolved=False,
        )

    def test_anonymous_user_cannot_access_anomaly_create_page(self):
        response = self.client.get(
            reverse("anomaly_create", args=[self.recording.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_access_anomaly_create_page(self):
        self.client.force_login(self.flagger)

        response = self.client.get(
            reverse("anomaly_create", args=[self.recording.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recording.species.common_name)

    def test_unrelated_citizen_cannot_resolve_anomaly(self):
        self.client.force_login(self.other_citizen)

        response = self.client.post(
            reverse("anomaly_resolve", args=[self.anomaly.pk]),
            follow=True,
        )

        self.anomaly.refresh_from_db()

        self.assertFalse(self.anomaly.resolved)
        self.assertContains(response, "You do not have permission to resolve this anomaly.")

    def test_original_flagger_can_resolve_own_anomaly(self):
        self.client.force_login(self.flagger)

        response = self.client.post(
            reverse("anomaly_resolve", args=[self.anomaly.pk]),
            follow=True,
        )

        self.anomaly.refresh_from_db()

        self.assertTrue(self.anomaly.resolved)
        self.assertEqual(self.anomaly.resolved_by, self.flagger)
        self.assertContains(response, "Anomaly resolved successfully.")

    def test_approved_researcher_can_resolve_anomaly(self):
        self.client.force_login(self.researcher)

        response = self.client.post(
            reverse("anomaly_resolve", args=[self.anomaly.pk]),
            follow=True,
        )

        self.anomaly.refresh_from_db()

        self.assertTrue(self.anomaly.resolved)
        self.assertEqual(self.anomaly.resolved_by, self.researcher)
        self.assertContains(response, "Anomaly resolved successfully.")