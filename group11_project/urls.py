"""
URL configuration for group11_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from group11_app import views

"""
Current URL patterns are for testing template page routing. 
"""
urlpatterns = [
    path('admin/', admin.site.urls),

    # homepage
    path('', views.home, name='home'),

    # recordings
    path('recordings/', views.recording_list, name='recording_list'),
    path('recordings/submit/', views.recording_create, name='recording_create'),
    path('recordings/<int:pk>/', views.recording_detail, name='recording_detail'),

    # species
    path('species/', views.species_list, name='species_list'),
    path('species/<int:pk>/', views.species_detail, name='species_detail'),

    # anomalies
    path('anomalies/', views.anomaly_list, name='anomaly_list'),
    path('recordings/<int:pk>/flag/', views.anomaly_create, name='anomaly_create'),
]