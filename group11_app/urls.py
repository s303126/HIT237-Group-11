from django.urls import path
from .views import HomepageView, SubmitRecordingView, ViewSubmissionsView, FlagAnomalyView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),
    path("submit/", SubmitRecordingView.as_view(), name="submit_recording"),
    path("submissions/", ViewSubmissionsView.as_view(), name="view_submissions"),
    path("flag/<int:recording_id>/", FlagAnomalyView.as_view(), name="flag_anomaly"),
]