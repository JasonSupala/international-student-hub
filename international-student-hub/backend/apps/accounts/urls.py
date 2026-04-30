"""
accounts/urls.py
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import RegisterView, logout_view, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", TokenObtainPairView.as_view(), name="auth-login"),   # Returns access + refresh
    path("logout/", logout_view, name="auth-logout"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
]
