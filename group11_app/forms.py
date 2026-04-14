from django import forms
from .models import Recording

class RecordingForm(forms.ModelForm):
    class Meta:
        model = Recording
        fields = [
            "species", "audio_file", "date_recorded",
            "latitude", "longitude", "location_name",
            "confidence_score", "notes"
        ]