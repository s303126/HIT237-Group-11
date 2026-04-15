from django.urls import path
from .views import AnomalyListView, ViewSubmissionsView
from .views import HomepageView
from .views import RecordingCreateView
from .views import SpeciesListView
from .views import SpeciesDetailView
from .views import RecordingDetailView
from .views import AnomalyCreateView
from .views import AnomalyResolveView
from .views import RecordingUpdateView
from .views import RecordingDeleteView

urlpatterns = [
    path("recordings/", ViewSubmissionsView.as_view(), name="recording_list"),
    path("species/", SpeciesListView.as_view(), name="species_list"),
    path("species/<int:pk>/", SpeciesDetailView.as_view(), name="species_detail"),
    path("recordings/create/", RecordingCreateView.as_view(), name="recording_create"),
    path("recordings/<int:pk>/", RecordingDetailView.as_view(), name="recording_detail"),   
    path("anomalies/", AnomalyListView.as_view(), name="anomaly_list"),
    path("anomalies/create/<int:pk>/", AnomalyCreateView.as_view(), name="anomaly_create"),
    path("anomalies/resolve/<int:pk>/", AnomalyResolveView.as_view(), name="anomaly_resolve"),
    path("", HomepageView.as_view(), name="home"),
    path("recordings/<int:pk>/edit/", RecordingUpdateView.as_view(), name="recording_update"),
    path("recordings/<int:pk>/delete/", RecordingDeleteView.as_view(), name="recording_delete"),
]