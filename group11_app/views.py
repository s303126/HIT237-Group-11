from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic import CreateView
from django.views.generic import DetailView
from .models import Anomaly, Recording
from .models import User
from .models import Species
from django.views import View
from django.shortcuts import get_object_or_404, redirect



from django.urls import reverse_lazy

from django.contrib.auth import get_user_model
User = get_user_model()


from .models import User

"""
Current views are for testing template page routing.
"""
#def home(request):
#    return render(request, "home.html")
class HomepageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_recordings"] = Recording.objects.get_timeline()[:3]
        return context

#def recording_list(request):
#    return render(request, "recordings/recording_list.html")
class ViewSubmissionsView(ListView):
    queryset = Recording.objects.get_timeline()
    template_name = "recordings/recording_list.html"
    context_object_name = "recordings"

#def recording_create(request):
#    return render(request, "recordings/recording_form.html")


class RecordingCreateView(CreateView):
    model = Recording
    template_name = "recordings/recording_form.html"
    fields = [
        "species", "date_recorded", "location_name",
        "latitude", "longitude", "confidence_score",
        "audio_file", "notes",
    ]
    success_url = reverse_lazy("recording_list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            # Cast to your custom User model
            form.instance.user = User.objects.get(pk=self.request.user.pk)
        else:
            guest_user, created = User.objects.get_or_create(
                username="guest",
                defaults={"role": "citizen_scientist"}
            )
            form.instance.user = guest_user
        return super().form_valid(form)

class RecordingDetailView(DetailView):
    model = Recording
    template_name = "recordings/recording_detail.html"
    context_object_name = "recording"


#def recording_detail(request, pk):
#    return render(request, "recordings/recording_detail.html")

#def species_list(request):
#    return render(request, "species/species_list.html")

class SpeciesListView(ListView):
    queryset = Species.objects.get_with_recording_counts()
    template_name = "species/species_list.html"
    context_object_name = "species_list"

#class ViewSpeciesView(ListView):
#    queryset = Recording.objects.get_timeline()
#    template_name = "recordings/recording_list.html"
#    context_object_name = "recordings"

#class SpeciesListView(ListView):
#    queryset = Species.objects.get_with_recording_counts()
#    template_name = "species/species_list.html"
#    context_object_name = "species"

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
#def species_detail(request, pk):
#    return render(request, "species/species_detail.html")

#def anomaly_list(request):
#    return render(request, "anomalies/anomaly_list.html")

#def anomaly_create(request, pk):
#    return render(request, "anomalies/anomaly_form.html")

#class AnomalyListView(ListView):
#    queryset = Anomaly.objects.select_related("recording__species", "flagged_by")
#    template_name = "anomalies/anomaly_list.html"
#    context_object_name = "anomalies"

class AnomalyListView(ListView):
    model = Anomaly
    template_name = "anomalies/anomaly_list.html"
    context_object_name = "anomalies"

    def get_queryset(self):
        # Use your custom manager method
        return Anomaly.objects.get_unresolved()


#class AnomalyCreateView(CreateView):
#    model = Anomaly
#    template_name = "anomalies/anomaly_form.html"
#    fields = ["recording", "reason", "description"]  # keep it simple
#    success_url = reverse_lazy("anomaly_list")

#    def form_valid(self, form):
#        recording_id = self.kwargs["pk"]
#        form.instance.recording_id = recording_id
#        if self.request.user.is_authenticated:
#            form.instance.flagged_by = self.request.user
#        return super().form_valid(form)

    
class AnomalyCreateView(CreateView):
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

        if self.request.user.is_authenticated:
            form.instance.flagged_by = User.objects.get(pk=self.request.user.pk)
        else:
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
