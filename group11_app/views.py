from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from .models import Anomaly, Recording, User, Species
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
User = get_user_model()


from .models import User


class HomepageView(TemplateView):
    template_name = "home.html"

class ViewSubmissionsView(ListView):
    queryset = Recording.objects.get_timeline()
    template_name = "recordings/recording_list.html"
    context_object_name = "recordings"

class RecordingCreateView(CreateView):
    model = Recording
    template_name = "recordings/recording_form.html"
    fields = [
        "species", "date_recorded", "location_name",
        "latitude", "longitude", "confidence_score",
        "audio_file", "notes", "role",   # <-- add role here
    ]
    success_url = reverse_lazy("recording_list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        else:
            role = form.cleaned_data['role']
            guest_username = f"guest_{role}"
            guest_user, created = User.objects.get_or_create(
                username=guest_username,
                defaults={"is_active": True}
            )
            form.instance.user = guest_user
        return super().form_valid(form)

class RecordingDetailView(DetailView):
    model = Recording
    template_name = "recordings/recording_detail.html"
    context_object_name = "recording"

class SpeciesListView(ListView):
    queryset = Species.objects.get_with_recording_counts()
    template_name = "species/species_list.html"
    context_object_name = "species"

class SpeciesDetailView(DetailView):
    model = Species
    template_name = "species/species_detail.html"
    context_object_name = "species"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add extra context for recordings
        context["recent_recordings"] = self.object.get_recent_recordings()
        context["flagged_recordings"] = self.object.get_flagged_recordings()
        return context

class AnomalyListView(ListView):
    model = Anomaly
    template_name = "anomalies/anomaly_list.html"
    context_object_name = "anomalies"

    def get_queryset(self):
        # Use your custom manager method
        return Anomaly.objects.get_unresolved()
    
class AnomalyCreateView(CreateView):
    model = Anomaly
    template_name = "anomalies/anomaly_form.html"
    fields = ["reason"]  # add description if you want
    success_url = reverse_lazy("anomaly_list")

    def form_valid(self, form):
        # tie anomaly to the recording being flagged
        recording_id = self.kwargs["pk"]
        form.instance.recording_id = recording_id

        if self.request.user.is_authenticated:
            # unwrap lazy user and assign
            form.instance.flagged_by = User.objects.get(pk=self.request.user.pk)
        else:
            # create or reuse a guest user
            guest_user, _ = User.objects.get_or_create(
                username="guest",
                defaults={"role": "citizen_scientist"}
            )
            form.instance.flagged_by = guest_user

        return super().form_valid(form)


class AnomalyResolveView(View):
    def post(self, request, pk):
        anomaly = get_object_or_404(Anomaly, pk=pk)

        if request.user.is_authenticated:
            # unwrap the lazy user
            user = User.objects.get(pk=request.user.pk)
        else:
            # create or reuse guest user
            user, _ = User.objects.get_or_create(
                username="guest",
                defaults={"role": "citizen_scientist"}
            )

        anomaly.resolve(user)
        return redirect(reverse_lazy("anomaly_list"))
