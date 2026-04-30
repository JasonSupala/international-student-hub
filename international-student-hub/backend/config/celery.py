"""
config/celery.py — Celery application instance.
This file is imported by config/__init__.py so Celery starts with Django.
"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("ish")

# Read Celery config from Django settings (keys prefixed with CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in all installed apps
app.autodiscover_tasks()
