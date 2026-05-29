from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views import View
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Anomaly, Recording, User, Species
from accounts.mixins import StaffRequiredMixin, OwnerOrStaffRequiredMixin
User = get_user_model()

from .services import validate_recording_duplicate, validate_anomaly_duplicate, validate_audio_file, validate_anomaly_not_resolved
from .exceptions import DuplicateRecording, DuplicateAnomaly, InvalidAudioFileLength, AnomalyAlreadyResolved

from django.db.models import Q

#404 error handler
def custom_404(request, exception):
    return render(request, '404.html', status=404)


#search
def search(request):
    #Search view that handles recordings, species, and anomalies. Uses query parameter 'type' to determine which search to perform.

    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('type', 'recordings')  # Default to recordings
    
    if query:
        if search_type == 'recordings':
            results = Recording.objects.search(query)
        elif search_type == 'species':
            results = Species.objects.search(query)
        elif search_type == 'anomalies':
            results = Anomaly.objects.search(query)
    else:     
        results = []
    
    return render(request, 'search.html', {'query': query, 'search_type': search_type, 'results': results})
 
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flagged_users'] = Recording.objects.get_users_with_high_flags()
        return context


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
        recording = Recording.objects.get(id=recording_id)
        
        try:
            validate_anomaly_duplicate(
                recording=recording,
                reason=form.cleaned_data["reason"],
            )
        except DuplicateAnomaly as e:
            form.add_error("reason", str(e))
            return self.form_invalid(form)
        
        form.instance.recording_id = recording_id
        form.instance.flagged_by = self.request.user
        return super().form_valid(form)


class AnomalyResolveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        anomaly = get_object_or_404(Anomaly, pk=pk)
        
        # Check permission: researcher OR the user who flagged it
        if not request.user.has_researcher_access() and anomaly.flagged_by != request.user:
            return HttpResponseForbidden("You do not have permission to resolve this anomaly.")
        
        try:
            validate_anomaly_not_resolved(anomaly)
        except AnomalyAlreadyResolved as e:
            messages.error(request, str(e))
            return redirect(reverse_lazy("anomaly_list"))
        
        anomaly.resolve(request.user)
        return redirect(reverse_lazy("anomaly_list"))

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
        try:
            validate_recording_duplicate(
                species=form.cleaned_data["species"],
                date_recorded=form.cleaned_data["date_recorded"],
                location_name=form.cleaned_data["location_name"],
                latitude=form.cleaned_data["latitude"],
                longitude=form.cleaned_data["longitude"],
            )
        except DuplicateRecording as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        
        try:
            validate_audio_file(form.cleaned_data["audio_file"])
        except InvalidAudioFileLength as e:
            form.add_error("audio_file", str(e))
            return self.form_invalid(form)
        
        form.instance.user = self.request.user
        if self.request.user.has_researcher_access():
            form.instance.status = 'approved'
        return super().form_valid(form)

class RecordingUpdateView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, UpdateView):
    model = Recording
    template_name = "recordings/recording_form.html"
    fields = [
        "species", "date_recorded", "location_name",
        "latitude", "longitude", "confidence_score",
        "audio_file", "notes",
    ]
    success_url = reverse_lazy("recording_list")

    def form_valid(self, form):
        try:
            validate_recording_duplicate(
                species=form.cleaned_data["species"],
                date_recorded=form.cleaned_data["date_recorded"],
                location_name=form.cleaned_data["location_name"],
                latitude=form.cleaned_data["latitude"],
                longitude=form.cleaned_data["longitude"],
                exclude_id=self.object.id,
            )
        except DuplicateRecording as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        
        return super().form_valid(form)

class ReviewQueueView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    template_name = "recordings/recording_review.html"
    context_object_name = "recordings"

    def get_queryset(self):
        status_filter = self.request.GET.get('status', 'under_review')
        if status_filter == 'approved':
            return Recording.objects.get_recently_approved()
        elif status_filter == 'rejected':
            return Recording.objects.get_rejected()
        return Recording.objects.get_pending_review()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = self.request.GET.get('status', 'under_review')
        context['rejected_users'] = Recording.objects.get_users_with_high_rejections()
        return context

class RecordingApproveView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        recording = get_object_or_404(Recording, pk=pk)
        recording.approve()
        return redirect('review_queue')
    
class RecordingRejectView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        recording = get_object_or_404(Recording, pk=pk, status='under_review')
        recording.reject()
        return redirect('review_queue')

class RecordingRestoreView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        recording = get_object_or_404(Recording, pk=pk, status='rejected')
        recording.approve()
        return redirect('review_queue')

class RecordingDetailView(DetailView):
    model = Recording
    template_name = "recordings/recording_detail.html"
    context_object_name = "recording"


class RecordingDeleteView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, DeleteView):
    model = Recording
    template_name = "recordings/recording_confirm_delete.html"
    success_url = reverse_lazy("recording_list")
