from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .helpers import (
    create_anomaly,
    create_approved_researcher,
    create_citizen,
    create_recording,
    create_rejected_recording,
    create_under_review_recording,
)


class PublicReadPermissionTests(TestCase):
    def test_anonymous_user_can_view_homepage(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_can_view_recording_timeline(self):
        response = self.client.get(reverse("recording_list"))

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_can_view_species_list(self):
        response = self.client.get(reverse("species_list"))

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_can_view_anomaly_list(self):
        response = self.client.get(reverse("anomaly_list"))

        self.assertEqual(response.status_code, 200)


class RecordingSubmissionPermissionTests(TestCase):
    def test_anonymous_user_cannot_access_recording_create_page(self):
        response = self.client.get(reverse("recording_create"))

        self.assertEqual(response.status_code, 302)

    def test_logged_in_citizen_can_access_recording_create_page(self):
        citizen = create_citizen()
        self.client.force_login(citizen)

        response = self.client.get(reverse("recording_create"))

        self.assertEqual(response.status_code, 200)

    def test_approved_researcher_can_access_recording_create_page(self):
        researcher = create_approved_researcher()
        self.client.force_login(researcher)

        response = self.client.get(reverse("recording_create"))

        self.assertEqual(response.status_code, 200)


class RecordingModerationPermissionTests(TestCase):
    def setUp(self):
        self.owner = create_citizen(username="owner")
        self.other_citizen = create_citizen(username="other_citizen")
        self.researcher = create_approved_researcher(username="researcher")
        self.recording = create_recording(user=self.owner)

    def test_anonymous_user_cannot_access_recording_edit_page(self):
        response = self.client.get(
            reverse("recording_update", args=[self.recording.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_unrelated_citizen_cannot_access_recording_edit_page(self):
        self.client.force_login(self.other_citizen)

        response = self.client.get(
            reverse("recording_update", args=[self.recording.pk])
        )

        self.assertIn(response.status_code, [302, 403])

    def test_approved_researcher_can_access_recording_edit_page(self):
        self.client.force_login(self.researcher)

        response = self.client.get(
            reverse("recording_update", args=[self.recording.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_access_recording_delete_page(self):
        response = self.client.get(
            reverse("recording_delete", args=[self.recording.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_unrelated_citizen_cannot_access_recording_delete_page(self):
        self.client.force_login(self.other_citizen)

        response = self.client.get(
            reverse("recording_delete", args=[self.recording.pk])
        )

        self.assertIn(response.status_code, [302, 403])

    def test_approved_researcher_can_access_recording_delete_page(self):
        self.client.force_login(self.researcher)

        response = self.client.get(
            reverse("recording_delete", args=[self.recording.pk])
        )

        self.assertEqual(response.status_code, 200)


class ReviewQueuePermissionTests(TestCase):
    def setUp(self):
        self.citizen = create_citizen(username="citizen")
        self.researcher = create_approved_researcher(username="researcher")
        self.pending_recording = create_under_review_recording(user=self.citizen)
        self.rejected_recording = create_rejected_recording(user=self.citizen)

    def test_anonymous_user_cannot_access_review_queue(self):
        response = self.client.get(reverse("review_queue"))

        self.assertEqual(response.status_code, 302)

    def test_citizen_cannot_access_review_queue(self):
        self.client.force_login(self.citizen)

        response = self.client.get(reverse("review_queue"))

        self.assertIn(response.status_code, [302, 403])

    def test_approved_researcher_can_access_review_queue(self):
        self.client.force_login(self.researcher)

        response = self.client.get(reverse("review_queue"))

        self.assertEqual(response.status_code, 200)

    def test_citizen_cannot_approve_recording(self):
        self.client.force_login(self.citizen)

        response = self.client.post(
            reverse("recording_approve", args=[self.pending_recording.pk])
        )

        self.pending_recording.refresh_from_db()

        self.assertNotEqual(self.pending_recording.status, "approved")
        self.assertIn(response.status_code, [302, 403])

    def test_approved_researcher_can_approve_recording(self):
        self.client.force_login(self.researcher)

        response = self.client.post(
            reverse("recording_approve", args=[self.pending_recording.pk])
        )

        self.pending_recording.refresh_from_db()

        self.assertEqual(self.pending_recording.status, "approved")
        self.assertEqual(response.status_code, 302)

    def test_citizen_cannot_reject_recording(self):
        self.client.force_login(self.citizen)

        response = self.client.post(
            reverse("recording_reject", args=[self.pending_recording.pk])
        )

        self.pending_recording.refresh_from_db()

        self.assertEqual(self.pending_recording.status, "under_review")
        self.assertIn(response.status_code, [302, 403])

    def test_approved_researcher_can_reject_recording(self):
        self.client.force_login(self.researcher)

        response = self.client.post(
            reverse("recording_reject", args=[self.pending_recording.pk])
        )

        self.pending_recording.refresh_from_db()

        self.assertEqual(self.pending_recording.status, "rejected")
        self.assertEqual(response.status_code, 302)

    def test_citizen_cannot_restore_recording(self):
        self.client.force_login(self.citizen)

        response = self.client.post(
            reverse("recording_restore", args=[self.rejected_recording.pk])
        )

        self.rejected_recording.refresh_from_db()

        self.assertEqual(self.rejected_recording.status, "rejected")
        self.assertIn(response.status_code, [302, 403])

    def test_approved_researcher_can_restore_recording(self):
        self.client.force_login(self.researcher)

        response = self.client.post(
            reverse("recording_restore", args=[self.rejected_recording.pk])
        )

        self.rejected_recording.refresh_from_db()

        self.assertEqual(self.rejected_recording.status, "approved")
        self.assertEqual(response.status_code, 302)


class AnomalyPermissionTests(TestCase):
    def setUp(self):
        self.flagger = create_citizen(username="flagger")
        self.other_citizen = create_citizen(username="other_citizen")
        self.researcher = create_approved_researcher(username="researcher")
        self.recording = create_recording(user=self.flagger)
        self.anomaly = create_anomaly(
            recording=self.recording,
            flagged_by=self.flagger,
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

    def test_unrelated_citizen_cannot_resolve_anomaly(self):
        self.client.force_login(self.other_citizen)

        response = self.client.post(
            reverse("anomaly_resolve", args=[self.anomaly.pk]),
            follow=True,
        )

        self.anomaly.refresh_from_db()
        messages = [str(message) for message in get_messages(response.wsgi_request)]

        self.assertFalse(self.anomaly.resolved)
        self.assertIn("You do not have permission to resolve this anomaly.", messages)

    def test_original_flagger_can_resolve_own_anomaly(self):
        self.client.force_login(self.flagger)

        response = self.client.post(
            reverse("anomaly_resolve", args=[self.anomaly.pk]),
            follow=True,
        )

        self.anomaly.refresh_from_db()
        messages = [str(message) for message in get_messages(response.wsgi_request)]

        self.assertTrue(self.anomaly.resolved)
        self.assertEqual(self.anomaly.resolved_by, self.flagger)
        self.assertIn("Anomaly resolved successfully.", messages)

    def test_approved_researcher_can_resolve_anomaly(self):
        self.client.force_login(self.researcher)

        response = self.client.post(
            reverse("anomaly_resolve", args=[self.anomaly.pk]),
            follow=True,
        )

        self.anomaly.refresh_from_db()
        messages = [str(message) for message in get_messages(response.wsgi_request)]

        self.assertTrue(self.anomaly.resolved)
        self.assertEqual(self.anomaly.resolved_by, self.researcher)
        self.assertIn("Anomaly resolved successfully.", messages)