from django.shortcuts import render, redirect, get_object_or_404
from .models import Recording, Anomaly
from .forms import RecordingForm

def homepage(request):
    return render(request, "index.html")

def submit_recording(request):
    if request.method == "POST":
        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            recording = form.save(commit=False)
            recording.user = request.user
            recording.save()
            return redirect("view_submissions")
    else:
        form = RecordingForm()
    return render(request, "submitrecording.html", {"form": form})

def view_submissions(request):
    recordings = Recording.objects.order_by("-date_recorded")
    return render(request, "recentrecordings.html", {"recordings": recordings})

def flag_anomaly(request, recording_id):
    recording = get_object_or_404(Recording, id=recording_id)
    if request.method == "POST":
        reason = request.POST.get("reason", "other")
        description = request.POST.get("description", "")
        Anomaly.objects.create(
            recording=recording,
            flagged_by=request.user,
            reason=reason,
            description=description
        )
        recording.flag(reason)
        return redirect("view_submissions")
    return render(request, "flag_anomaly.html", {"recording": recording})