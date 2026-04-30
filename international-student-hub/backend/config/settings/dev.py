"""
dev.py — Development-only settings.
Run with: DJANGO_SETTINGS_MODULE=config.settings.dev
"""

from .base import *  # noqa: F401, F403

# --------------------------------------------------------------------------
# Development Overrides
# --------------------------------------------------------------------------

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# --------------------------------------------------------------------------
# CORS — Allow the local React dev server (Vite default port 5173)
# --------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# --------------------------------------------------------------------------
# Django Debug Toolbar (optional but useful)
# --------------------------------------------------------------------------

# Uncomment if you install django-debug-toolbar:
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# INTERNAL_IPS = ["127.0.0.1"]

# --------------------------------------------------------------------------
# Email — Print to console instead of sending real emails in dev
# --------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --------------------------------------------------------------------------
# Logging — Show SQL queries in the terminal during development
# --------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",  # Set to "INFO" to hide SQL queries
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
