"""
accounts/serializers.py — Serializers for auth and user profile endpoints.
"""

from io import BytesIO
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, features
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile


MAX_AVATAR_UPLOAD_SIZE = 5 * 1024 * 1024
MAX_AVATAR_STORED_SIZE = 512 * 1024
MAX_AVATAR_DIMENSION = 512


class AvatarImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if getattr(data, "size", 0) > MAX_AVATAR_UPLOAD_SIZE:
            raise serializers.ValidationError("File too large. Maximum avatar size is 5MB.")
        return super().to_internal_value(data)


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
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "is_staff", "is_superuser", "profile",
        ]
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
    Includes an access token; refresh is set in an HttpOnly cookie.
    """
    user = UserSerializer(read_only=True)
    access = serializers.CharField(read_only=True)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Allows users to update their own profile via PATCH /api/v1/auth/profile/.
    Nested profile fields are written through to UserProfile.
    """
    # Expose top-level User fields inline
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    avatar = AvatarImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "first_name", "last_name", "email",
            "country", "university", "arrival_date",
            "bio", "avatar", "preferred_language",
        ]

    def validate_avatar(self, avatar):
        try:
            avatar.seek(0)
            with Image.open(avatar) as image:
                image.verify()
            avatar.seek(0)
            with Image.open(avatar) as image:
                image = ImageOps.exif_transpose(image)
                image.load()
                return _compress_avatar(image, avatar.name)
        except serializers.ValidationError:
            raise
        except Exception:
            raise serializers.ValidationError("Upload a valid image file.")
        finally:
            try:
                avatar.seek(0)
            except Exception:
                pass

    def update(self, instance, validated_data):
        old_avatar = instance.avatar if validated_data.get("avatar") and instance.avatar else None

        # Handle nested User fields
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if old_avatar and old_avatar.name != instance.avatar.name:
            old_avatar.delete(save=False)

        return instance


def _compress_avatar(image, original_name):
    image.thumbnail((MAX_AVATAR_DIMENSION, MAX_AVATAR_DIMENSION), Image.Resampling.LANCZOS)

    has_transparency = image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )
    suffix = f"avatar-{uuid4().hex}"

    if has_transparency and features.check("webp"):
        data = _encode_with_quality(image.convert("RGBA"), "WEBP")
        filename = f"{suffix}.webp"
    elif has_transparency:
        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        data = buffer.getvalue()
        filename = f"{suffix}.png"
    else:
        data = _encode_with_quality(image.convert("RGB"), "JPEG")
        filename = f"{suffix}.jpg"

    return ContentFile(data, name=filename)


def _encode_with_quality(image, image_format):
    quality_values = range(85, 35, -10)
    current = image
    data = b""

    while True:
        for quality in quality_values:
            buffer = BytesIO()
            current.save(buffer, format=image_format, optimize=True, quality=quality)
            data = buffer.getvalue()
            if len(data) <= MAX_AVATAR_STORED_SIZE:
                return data

        width, height = current.size
        if max(width, height) <= 128:
            return data

        scale = max(128 / max(width, height), 0.85)
        current = current.resize(
            (max(1, int(width * scale)), max(1, int(height * scale))),
            Image.Resampling.LANCZOS,
        )
