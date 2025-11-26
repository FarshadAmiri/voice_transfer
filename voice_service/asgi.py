"""
ASGI config for voice_service project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voice_service.settings')

application = get_asgi_application()
