"""
config/urls.py — Root URL configuration.

All API routes are versioned under /api/v1/ for future compatibility.
Each app registers its own router, which is included here.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# JWT token endpoints (login / refresh / verify)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Django admin (useful for content management)
    path("admin/", admin.site.urls),

    # -----------------------------------------------------------------------
    # Auth endpoints — JWT-based, no sessions
    # -----------------------------------------------------------------------
    # POST /api/v1/auth/register/       → create account
    # POST /api/v1/auth/login/          → returns access + refresh tokens
    # POST /api/v1/auth/token/refresh/  → exchange refresh for new access token
    # POST /api/v1/auth/token/verify/   → check if token is still valid
    # POST /api/v1/auth/logout/         → blacklist the refresh token
    # GET  /api/v1/auth/profile/        → current user's profile
    path("api/v1/auth/", include("apps.accounts.urls")),

    # JWT token management (built-in simplejwt views)
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # -----------------------------------------------------------------------
    # Feature app endpoints
    # -----------------------------------------------------------------------
    path("api/v1/checklist/", include("apps.checklist.urls")),
    path("api/v1/directory/", include("apps.directory.urls")),
    path("api/v1/community/", include("apps.community.urls")),
    path("api/v1/bot/", include("apps.bot.urls")),
]

# Serve uploaded media files in development (in prod, use a CDN/object storage)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
