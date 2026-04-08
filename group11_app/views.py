from django.shortcuts import render

"""
Current views are for testing template page routing.
"""
def home(request):
    return render(request, "home.html")

def recording_list(request):
    return render(request, "recordings/recording_list.html")

def recording_create(request):
    return render(request, "recordings/recording_form.html")

def recording_detail(request, pk):
    return render(request, "recordings/recording_detail.html")

def species_list(request):
    return render(request, "species/species_list.html")

def species_detail(request, pk):
    return render(request, "species/species_detail.html")

def anomaly_list(request):
    return render(request, "anomalies/anomaly_list.html")

def anomaly_create(request, pk):
    return render(request, "anomalies/anomaly_form.html")