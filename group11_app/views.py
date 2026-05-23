from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Anomaly, Recording, User, Species
from accounts.mixins import StaffRequiredMixin, OwnerOrStaffRequiredMixin
User = get_user_model()

from .models import User


class HomepageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_recordings"] = Recording.objects.get_timeline()[:3]
        return context


class ViewSubmissionsView(ListView):
    queryset = Recording.objects.get_timeline()
    template_name = "recordings/recording_list.html"
    context_object_name = "recordings"


class RecordingCreateView(LoginRequiredMixin, CreateView):
    model = Recording
    template_name = "recordings/recording_form.html"
    fields = [
        "species", "date_recorded", "location_name",
        "latitude", "longitude", "confidence_score",
        "audio_file", "notes",
    ]
    success_url = reverse_lazy("recording_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RecordingDetailView(DetailView):
    model = Recording
    template_name = "recordings/recording_detail.html"
    context_object_name = "recording"


class SpeciesListView(ListView):
    queryset = Species.objects.get_with_recording_counts()
    template_name = "species/species_list.html"
    context_object_name = "species_list"


class SpeciesDetailView(DetailView):
    model = Species
    template_name = "species/species_detail.html"
    context_object_name = "species"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_recordings"] = self.object.get_recent_recordings()
        context["flagged_recordings"] = self.object.get_flagged_recordings()
        return context


class AnomalyListView(ListView):
    model = Anomaly
    template_name = "anomalies/anomaly_list.html"
    context_object_name = "anomalies"

    def get_queryset(self):
        return Anomaly.objects.get_unresolved()


class AnomalyCreateView(LoginRequiredMixin, CreateView):
    model = Anomaly
    template_name = "anomalies/anomaly_form.html"
    fields = ["reason"]
    success_url = reverse_lazy("anomaly_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recording"] = get_object_or_404(Recording, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        recording_id = self.kwargs["pk"]
        form.instance.recording_id = recording_id
        form.instance.flagged_by = self.request.user
        return super().form_valid(form)


class AnomalyResolveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        anomaly = get_object_or_404(Anomaly, pk=pk)
        
        # Check permission: researcher OR the user who flagged it
        if not request.user.has_researcher_access() and anomaly.flagged_by != request.user:
            return HttpResponseForbidden("You do not have permission to resolve this anomaly.")
        
        anomaly.resolve(request.user)
        return redirect(reverse_lazy("anomaly_list"))
    
class RecordingUpdateView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, UpdateView):
    model = Recording
    template_name = "recordings/recording_form.html"
    fields = [
        "species", "date_recorded", "location_name",
        "latitude", "longitude", "confidence_score",
        "audio_file", "notes",
    ]
    success_url = reverse_lazy("recording_list")


class RecordingDeleteView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, DeleteView):
    model = Recording
    template_name = "recordings/recording_confirm_delete.html"
    success_url = reverse_lazy("recording_list")