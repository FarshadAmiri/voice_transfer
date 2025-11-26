"""
URL configuration for voice_service project.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('voice_clone_api.urls')),
]
