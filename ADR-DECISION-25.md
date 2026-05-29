### ADR-25: Submission review system for citizen scientist recordings

**Date:** 29/05/2026

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**
Claude AI used to assist with implementation.

**Context:**
All recordings appeared on the public timeline immediately regardless of who submitted them. The anomaly flagging system allowed users to report issues after a recording was visible, There was no quality control process for citizen scientist submissions before they appeared on the timeline.

**Alternatives considered:**

- Option 1: All submissions appear immediately with no review. Simple but no quality control.

- Option 2: Require all submissions to be reviewed including researchers. Unnecessary for verified researchers.

- Option 3: Only citizen scientist submissions require review. Researcher submissions are auto-approved.

**Decision:**
Add a status field to Recording with three states: 'under review', 'approved' and 'rejected'. Citizen scientist submissions default to 'under review' and are hidden from the timeline until approved. A Review Queue page enables researchers to approve, reject, restore or permanently delete recordings.

**Code reference:**
group11_app/models.py: Recording.status, Recording.approved_at
group11_app/views.py: ReviewQueueView, RecordingApproveView, RecordingRejectView, RecordingRestoreView
group11_app/templates/recordings/recording_review.html

**Consequences:**
Citizen scientist recordings require researcher approval before appearing on the public timeline, increasing researcher moderation responsibility. Existing recordings default to 'under review' and need manual approval. 

The review serves as an initial screening for irrelevant or inappropriate submissions, while the anomaly flagging system remains relevant as ongoing quality control for issues such as incorrect species identification, location errors or poor audio quality.