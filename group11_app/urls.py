from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("submit/", views.submit_recording, name="submit_recording"),
    path("submissions/", views.view_submissions, name="view_submissions"),
    path("flag/<int:recording_id>/", views.flag_anomaly, name="flag_anomaly"),
]