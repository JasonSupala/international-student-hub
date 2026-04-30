"""
accounts/serializers.py — Serializers for auth and user profile endpoints.
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes the extended UserProfile fields."""

    class Meta:
        model = UserProfile
        fields = [
            "country", "university", "arrival_date",
            "bio", "avatar", "preferred_language",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """
    Read serializer for the User model.
    Nests the UserProfile as a sub-object.
    Used for GET /api/v1/auth/profile/
    """
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration serializer.
    Accepts password + password2 for confirmation, then creates the User.
    Returns JWT tokens immediately so the user is logged in after registering.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]  # Runs Django's built-in password strength checks
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirm password"
    )

    # Optional profile fields at registration time
    country = serializers.CharField(required=False, allow_blank=True)
    university = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "password2",
            "first_name", "last_name",
            "country", "university",
        ]

    def validate(self, attrs):
        """Confirm the two passwords match before creating the account."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Pop profile-specific fields before creating User
        country = validated_data.pop("country", "")
        university = validated_data.pop("university", "")
        validated_data.pop("password2")

        # create_user hashes the password (never store plaintext!)
        user = User.objects.create_user(**validated_data)

        # Update the auto-created UserProfile with additional info
        user.profile.country = country
        user.profile.university = university
        user.profile.save()

        return user


class RegisterResponseSerializer(serializers.Serializer):
    """
    Response body returned after successful registration.
    Includes JWT tokens so the user doesn't need to log in separately.
    """
    user = UserSerializer(read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Allows users to update their own profile via PATCH /api/v1/auth/profile/.
    Nested profile fields are written through to UserProfile.
    """
    # Expose top-level User fields inline
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = UserProfile
        fields = [
            "first_name", "last_name", "email",
            "country", "university", "arrival_date",
            "bio", "avatar", "preferred_language",
        ]

    def update(self, instance, validated_data):
        # Handle nested User fields
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
