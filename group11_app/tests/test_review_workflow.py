from django.test import TestCase
from django.urls import reverse

from group11_app.models import Recording
from group11_app.services import get_review_queue_context

from .helpers import (
    create_approved_researcher,
    create_citizen,
    create_recording,
    create_rejected_recording,
    create_under_review_recording,
)


class RecordingTimelineWorkflowTests(TestCase):
    def test_only_approved_recordings_appear_in_timeline_manager(self):
        approved_recording = create_recording(status="approved")
        under_review_recording = create_under_review_recording()
        rejected_recording = create_rejected_recording()

        timeline = Recording.objects.get_timeline()

        self.assertIn(approved_recording, timeline)
        self.assertNotIn(under_review_recording, timeline)
        self.assertNotIn(rejected_recording, timeline)

        for recording in timeline:
            self.assertEqual(recording.status, "approved")

    def test_recording_list_page_shows_approved_recording(self):
        approved_recording = create_recording(status="approved")

        response = self.client.get(reverse("recording_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, approved_recording.species.common_name)

    def test_recording_list_page_hides_under_review_recording(self):
        under_review_recording = create_under_review_recording()

        response = self.client.get(reverse("recording_list"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, under_review_recording.species.common_name)

    def test_recording_list_page_hides_rejected_recording(self):
        rejected_recording = create_rejected_recording()

        response = self.client.get(reverse("recording_list"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, rejected_recording.species.common_name)


class ReviewQueueContextTests(TestCase):
    def test_default_review_queue_context_returns_under_review_recordings(self):
        pending_recording = create_under_review_recording()
        create_recording(status="approved")
        create_rejected_recording()

        context = get_review_queue_context()

        self.assertEqual(context["current_filter"], "under_review")
        self.assertIn(pending_recording, context["recordings"])

        for recording in context["recordings"]:
            self.assertEqual(recording.status, "under_review")

    def test_review_queue_context_returns_rejected_recordings(self):
        rejected_recording = create_rejected_recording()
        create_under_review_recording()
        create_recording(status="approved")

        context = get_review_queue_context(status_filter="rejected")

        self.assertEqual(context["current_filter"], "rejected")
        self.assertIn(rejected_recording, context["recordings"])

        for recording in context["recordings"]:
            self.assertEqual(recording.status, "rejected")

    def test_review_queue_context_returns_recently_approved_recordings(self):
        approved_recording = create_recording(status="approved")
        create_under_review_recording()
        create_rejected_recording()

        context = get_review_queue_context(status_filter="approved")

        self.assertEqual(context["current_filter"], "approved")
        self.assertIn(approved_recording, context["recordings"])

        for recording in context["recordings"]:
            self.assertEqual(recording.status, "approved")


class ReviewQueueViewWorkflowTests(TestCase):
    def setUp(self):
        self.citizen = create_citizen(username="citizen")
        self.researcher = create_approved_researcher(username="researcher")
        self.pending_recording = create_under_review_recording(user=self.citizen)
        self.rejected_recording = create_rejected_recording(user=self.citizen)
        self.approved_recording = create_recording(
            user=self.researcher,
            status="approved",
        )

    def test_researcher_review_queue_defaults_to_pending_filter(self):
        self.client.force_login(self.researcher)

        response = self.client.get(reverse("review_queue"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pending_recording.species.common_name)
        self.assertNotContains(response, self.rejected_recording.species.common_name)

    def test_researcher_can_view_rejected_filter(self):
        self.client.force_login(self.researcher)

        response = self.client.get(
            reverse("review_queue"),
            {"status": "rejected"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.rejected_recording.species.common_name)

    def test_researcher_can_view_recently_approved_filter(self):
        self.client.force_login(self.researcher)

        response = self.client.get(
            reverse("review_queue"),
            {"status": "approved"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.approved_recording.species.common_name)

    def test_approve_action_moves_recording_to_public_timeline(self):
        self.client.force_login(self.researcher)

        self.client.post(
            reverse("recording_approve", args=[self.pending_recording.pk])
        )

        self.pending_recording.refresh_from_db()

        self.assertEqual(self.pending_recording.status, "approved")
        self.assertIsNotNone(self.pending_recording.approved_at)

        timeline_response = self.client.get(reverse("recording_list"))
        self.assertContains(
            timeline_response,
            self.pending_recording.species.common_name,
        )

    def test_reject_action_keeps_recording_off_public_timeline(self):
        self.client.force_login(self.researcher)

        self.client.post(
            reverse("recording_reject", args=[self.pending_recording.pk])
        )

        self.pending_recording.refresh_from_db()

        self.assertEqual(self.pending_recording.status, "rejected")

        timeline_response = self.client.get(reverse("recording_list"))
        self.assertNotContains(
            timeline_response,
            self.pending_recording.species.common_name,
        )

    def test_restore_action_reapproves_rejected_recording(self):
        self.client.force_login(self.researcher)

        self.client.post(
            reverse("recording_restore", args=[self.rejected_recording.pk])
        )

        self.rejected_recording.refresh_from_db()

        self.assertEqual(self.rejected_recording.status, "approved")
        self.assertIsNotNone(self.rejected_recording.approved_at)