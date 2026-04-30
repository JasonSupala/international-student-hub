"""
base.py — Shared settings for all environments.
dev.py and prod.py import from here and override what they need.
Never put secrets here — use environment variables via django-environ.
"""

import os
from pathlib import Path
from datetime import timedelta
import environ

# --------------------------------------------------------------------------
# Path & Environment Setup
# --------------------------------------------------------------------------

# BASE_DIR points to the backend/ folder (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize django-environ and read .env file if it exists
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# --------------------------------------------------------------------------
# Core Django Settings
# --------------------------------------------------------------------------

SECRET_KEY = env("DJANGO_SECRET_KEY")

# Apps split into groups for readability
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",                  # Django REST Framework
    "rest_framework_simplejwt",        # JWT authentication
    "rest_framework_simplejwt.token_blacklist",  # For logout (token blacklist)
    "corsheaders",                     # CORS for React frontend
    "django_filters",                  # Filtering support for DRF
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.checklist",
    "apps.directory",
    "apps.community",
    "apps.bot",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",   # Must be before CommonMiddleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --------------------------------------------------------------------------
# Database — PostgreSQL
# --------------------------------------------------------------------------

DATABASES = {
    "default": env.db("DATABASE_URL")
    # DATABASE_URL format: postgres://user:password@host:port/dbname
}


# --------------------------------------------------------------------------
# Password Validation
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Taipei"     # Taiwan timezone
USE_I18N = True
USE_TZ = True


# --------------------------------------------------------------------------
# Static & Media Files
# --------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------------------------------
# Django REST Framework Configuration
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    # All endpoints require authentication by default.
    # Override per-view with AllowAny for public endpoints.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    # Pagination: return 20 items per page by default
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # Enable filtering, searching, and ordering globally
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}


# --------------------------------------------------------------------------
# JWT Configuration (djangorestframework-simplejwt)
# --------------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),   # Short-lived access token
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),       # Refresh valid for a week
    "ROTATE_REFRESH_TOKENS": True,      # Issue new refresh token on each refresh
    "BLACKLIST_AFTER_ROTATION": True,   # Blacklist old refresh tokens (requires token_blacklist app)
    "AUTH_HEADER_TYPES": ("Bearer",),   # Authorization: Bearer <token>
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


# --------------------------------------------------------------------------
# Redis Cache & Celery
# --------------------------------------------------------------------------

REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Celery — async task queue
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE


# --------------------------------------------------------------------------
# LINE Bot Settings
# --------------------------------------------------------------------------

LINE_CHANNEL_ACCESS_TOKEN = env("LINE_CHANNEL_ACCESS_TOKEN", default="")
LINE_CHANNEL_SECRET = env("LINE_CHANNEL_SECRET", default="")


# --------------------------------------------------------------------------
# CORS — Allow React frontend to call the API
# --------------------------------------------------------------------------

# In base.py we allow no origins; dev.py and prod.py set this properly.
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_CREDENTIALS = True  # Required for cookies/auth headers
