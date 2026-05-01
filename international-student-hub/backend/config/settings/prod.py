"""
prod.py — Production settings for Railway / Render deployment.
Run with: DJANGO_SETTINGS_MODULE=config.settings.prod

Security-hardened. Never set DEBUG=True here.
"""

from .base import *  # noqa: F401, F403
import environ

env = environ.Env()

# --------------------------------------------------------------------------
# Security
# --------------------------------------------------------------------------

DEBUG = False

# Railway/Render inject the public hostname as an env var
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[
    "international-student-hub-production.up.railway.app",
    ".up.railway.app",
    "localhost",
    "127.0.0.1",
])

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000        # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies — only send over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Prevent clickjacking
X_FRAME_OPTIONS = "DENY"

# --------------------------------------------------------------------------
# CORS — Your deployed React frontend URL
# --------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[]
)

# --------------------------------------------------------------------------
# Static Files — WhiteNoise serves static files in production without a CDN
# --------------------------------------------------------------------------

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --------------------------------------------------------------------------
# Email — Configure with SendGrid or similar for production
# --------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.sendgrid.net")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# --------------------------------------------------------------------------
# Logging — Write errors to stdout for Railway/Render log aggregation
# --------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
