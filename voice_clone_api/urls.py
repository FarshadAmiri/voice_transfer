"""
URL configuration for voice_clone_api app.
"""
from django.urls import path
from .views import VoiceCloneView, HealthCheckView

urlpatterns = [
    path('clone/', VoiceCloneView.as_view(), name='voice-clone'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
