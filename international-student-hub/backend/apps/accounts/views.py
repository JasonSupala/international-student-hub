"""
accounts/views.py — Auth endpoints: register, login, logout, profile.
"""

from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import status, generics
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import UserProfile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
)


def _refresh_cookie_kwargs():
    return {
        "path": settings.JWT_REFRESH_COOKIE_PATH,
        "httponly": settings.JWT_REFRESH_COOKIE_HTTPONLY,
        "secure": settings.JWT_REFRESH_COOKIE_SECURE,
        "samesite": settings.JWT_REFRESH_COOKIE_SAMESITE,
    }


def set_refresh_cookie(response, refresh_token):
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=max_age,
        **_refresh_cookie_kwargs(),
    )


def clear_refresh_cookie(response):
    response.delete_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        path=settings.JWT_REFRESH_COOKIE_PATH,
        samesite=settings.JWT_REFRESH_COOKIE_SAMESITE,
    )


class LoginView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)
        if refresh:
            set_refresh_cookie(response, refresh)
        return response


class CookieTokenRefreshView(generics.GenericAPIView):
    serializer_class = TokenRefreshSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh:
            return Response({"detail": "Refresh cookie is missing."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        new_refresh = data.pop("refresh", None)

        response = Response(data, status=status.HTTP_200_OK)
        if new_refresh:
            set_refresh_cookie(response, new_refresh)
        return response


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Create a new account and return JWT tokens immediately.
    No authentication required.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "user": UserSerializer(user, context={"request": request}).data,
                "access": str(refresh.access_token),
                "message": "Account created successfully. Welcome!",
            },
            status=status.HTTP_201_CREATED,
        )
        set_refresh_cookie(response, str(refresh))
        return response


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklists the refresh cookie and clears it.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        response = Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        clear_refresh_cookie(response)
        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/auth/profile/ → return the current user's full profile
    PATCH /api/v1/auth/profile/ → update profile fields

    Uses PATCH (partial update) — you don't need to send all fields at once.
    """
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method in ("PUT", "PATCH"):
            self.throttle_scope = "profile_update"
            return [ScopedRateThrottle()]
        return [throttle() for throttle in api_settings.DEFAULT_THROTTLE_CLASSES]

    def get_object(self):
        # Return the profile of the currently authenticated user
        return self.request.user.profile

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProfileUpdateSerializer
        return UserSerializer

    def get(self, request, *args, **kwargs):
        # Override to return the full User object (not just the profile)
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True  # Always allow partial updates
        return super().update(request, *args, **kwargs)
