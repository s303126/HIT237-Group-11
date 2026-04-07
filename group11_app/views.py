from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Recording, Anomaly
from .forms import RecordingForm

class HomepageView(TemplateView):
    template_name = "index.html"

class SubmitRecordingView(CreateView):
    model = Recording
    form_class = RecordingForm
    template_name = "submitrecording.html"
    success_url = reverse_lazy("view_submissions")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        else:
            # Assign a default user (e.g., a "guest" account)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            guest_user = User.objects.get(username="guest")
            form.instance.user = guest_user
        return super().form_valid(form)

class ViewSubmissionsView(ListView):
    model = Recording
    template_name = "recentrecordings.html"
    context_object_name = "recordings"
    ordering = ["-date_recorded"]

class FlagAnomalyView(CreateView):
    model = Anomaly
    fields = ["reason", "description"]
    template_name = "flag_anomaly.html"
    success_url = reverse_lazy("view_submissions")

    def form_valid(self, form):
        form.instance.recording_id = self.kwargs["recording_id"]
        form.instance.flagged_by = self.request.user
        return super().form_valid(form)