from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Anomaly, Recording, User, Species
from accounts.mixins import StaffRequiredMixin, OwnerOrStaffRequiredMixin
from django.core.paginator import Paginator

User = get_user_model()

from .services import validate_recording_duplicate, validate_anomaly_duplicate, validate_audio_file, validate_anomaly_not_resolved, create_recording, update_recording, approve_recording, reject_recording, restore_recording, flag_anomaly, resolve_anomaly, get_homepage_context, get_species_detail_context, get_anomaly_list_context, get_review_queue_context
from .exceptions import DuplicateRecording, DuplicateAnomaly, InvalidAudioFileLength, AnomalyAlreadyResolved

from django.db.models import Q

#404 error handler
def custom_404(request, exception):
    return render(request, '404.html', status=404)


#search
def search(request):
    #Search view that handles recordings, species, and anomalies. Uses query parameter 'type' to determine which search to perform.

    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('type', 'recordings')
    page_num = request.GET.get('page', 1)


    
    if query:
        if search_type == 'recordings':
            results = Recording.objects.search(query)
        elif search_type == 'species':
            results = Species.objects.search(query)
        elif search_type == 'anomalies':
            results = Anomaly.objects.search(query)
    else:     
        results = []
    
    paginator = Paginator(results, 5)
    page_obj = paginator.get_page(page_num)

    return render(request, 'search.html', {'query': query, 'search_type': search_type, 'results': page_obj.object_list if page_obj else results, 'paginator': paginator, 'page_obj': page_obj})


#Home
class HomepageView(TemplateView):
    template_name = "home.html"
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_homepage_context())
        return context


#Recordings
class ViewSubmissionsView(ListView):
    queryset = Recording.objects.get_timeline()
    template_name = "recordings/recording_list.html"
    context_object_name = "recordings"
    paginate_by = 5


class RecordingDetailView(DetailView):
    model = Recording
    template_name = "recordings/recording_detail.html"
    context_object_name = "recording"


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
        cd = form.cleaned_data
        try:
            create_recording(
                user=self.request.user,
                species=cd["species"],
                date_recorded=cd["date_recorded"],
                location_name=cd["location_name"],
                latitude=cd["latitude"],
                longitude=cd["longitude"],
                confidence_score=cd["confidence_score"],
                audio_file=cd["audio_file"],
                notes=cd.get("notes", ""),
            )
        except DuplicateRecording as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except InvalidAudioFileLength as e:
            form.add_error("audio_file", str(e))
            return self.form_invalid(form)
 
        return redirect(self.success_url)


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
        cd = form.cleaned_data
        try:
            update_recording(
                recording=self.object,
                species=cd["species"],
                date_recorded=cd["date_recorded"],
                location_name=cd["location_name"],
                latitude=cd["latitude"],
                longitude=cd["longitude"],
                confidence_score=cd["confidence_score"],
                audio_file=cd["audio_file"],
                notes=cd.get("notes", ""),
            )
        except DuplicateRecording as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
 
        return redirect(self.success_url)


class RecordingDeleteView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, DeleteView):
    model = Recording
    template_name = "recordings/recording_confirm_delete.html"
    success_url = reverse_lazy("recording_list")


#Review queue
class ReviewQueueView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    template_name = "recordings/recording_review.html"
    context_object_name = "recordings"
 
    def get_queryset(self):
        status_filter = self.request.GET.get('status', 'under_review')
        return get_review_queue_context(status_filter)["recordings"]
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status_filter = self.request.GET.get('status', 'under_review')
        queue_context = get_review_queue_context(status_filter)
        context['rejected_users'] = queue_context["rejected_users"]
        context['current_filter'] = queue_context["current_filter"]
        return context


class RecordingApproveView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        recording = get_object_or_404(Recording, pk=pk)
        approve_recording(recording)
        return redirect('review_queue')


class RecordingRejectView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        recording = get_object_or_404(Recording, pk=pk, status='under_review')
        reject_recording(recording)
        return redirect('review_queue')


class RecordingRestoreView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        recording = get_object_or_404(Recording, pk=pk, status='rejected')
        restore_recording(recording)
        return redirect('review_queue')


#Species
class SpeciesListView(ListView):
    queryset = Species.objects.get_with_recording_counts()
    template_name = "species/species_list.html"
    context_object_name = "species_list"
    paginate_by = 5


class SpeciesDetailView(DetailView):
    model = Species
    template_name = "species/species_detail.html"
    context_object_name = "species"
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_species_detail_context(self.object))
        return context


#Anomalies
class AnomalyListView(ListView):
    model = Anomaly
    template_name = "anomalies/anomaly_list.html"
    context_object_name = "anomalies"
    paginate_by = 5
 
    def get_queryset(self):
        return get_anomaly_list_context()["anomalies"]
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flagged_users'] = get_anomaly_list_context()["flagged_users"]
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
        recording = get_object_or_404(Recording, pk=self.kwargs["pk"])
        try:
            flag_anomaly(
                recording=recording,
                flagged_by=self.request.user,
                reason=form.cleaned_data["reason"],
            )
        except DuplicateAnomaly as e:
            form.add_error("reason", str(e))
            return self.form_invalid(form)
 
        return redirect(self.success_url)


class AnomalyResolveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        anomaly = get_object_or_404(Anomaly, pk=pk)
 
        if not request.user.has_researcher_access() and anomaly.flagged_by != request.user:
            messages.error(request, "You do not have permission to resolve this anomaly.")
            return redirect("anomaly_list")
 
        try:
            resolve_anomaly(anomaly=anomaly, resolved_by=request.user)
        except AnomalyAlreadyResolved as e:
            messages.error(request, str(e))
            return redirect("anomaly_list")
 
        messages.success(request, "Anomaly resolved successfully.")
        return redirect("anomaly_list")
