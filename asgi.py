"""
ASGI config for electronics_store project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electronics_store.settings')

application = get_asgi_application()