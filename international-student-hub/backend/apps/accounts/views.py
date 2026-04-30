"""
accounts/views.py — Auth endpoints: register, login, logout, profile.
"""

from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import UserProfile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Create a new account and return JWT tokens immediately.
    No authentication required.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user, context={"request": request}).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "Account created successfully. Welcome!",
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/v1/auth/logout/
    Blacklists the provided refresh token, effectively invalidating this session.
    The frontend should also delete the stored tokens from localStorage.

    Request body: { "refresh": "<refresh_token>" }
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response(
            {"error": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  # Requires token_blacklist app in INSTALLED_APPS
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/auth/profile/ → return the current user's full profile
    PATCH /api/v1/auth/profile/ → update profile fields

    Uses PATCH (partial update) — you don't need to send all fields at once.
    """
    permission_classes = [IsAuthenticated]

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
