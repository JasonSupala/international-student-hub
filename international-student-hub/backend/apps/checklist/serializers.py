"""
checklist/serializers.py
"""

from rest_framework import serializers
from .models import ChecklistCategory, ChecklistItem, UserChecklistProgress


class ChecklistItemSerializer(serializers.ModelSerializer):
    """Serializes a single checklist item. Does NOT include per-user progress."""

    class Meta:
        model = ChecklistItem
        fields = [
            "id", "category", "title", "description",
            "order", "resource_url", "university",
            "estimated_minutes", "is_active",
        ]


class ChecklistItemWithProgressSerializer(serializers.ModelSerializer):
    """
    Checklist item with the current user's completion status injected.
    Used in the authenticated checklist view so the frontend knows
    which items are done for the logged-in user.
    """
    completed = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistItem
        fields = [
            "id", "category", "title", "description",
            "order", "resource_url", "university",
            "estimated_minutes", "is_active",
            "completed", "completed_at",
        ]

    def get_completed(self, obj):
        """Return True/False for the requesting user."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.user_progress.filter(user=request.user, completed=True).exists()
        return False

    def get_completed_at(self, obj):
        """Return the timestamp when the user completed this item, or None."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            progress = obj.user_progress.filter(user=request.user).first()
            if progress:
                return progress.completed_at
        return None


class ChecklistCategorySerializer(serializers.ModelSerializer):
    """Category with all its items nested inside."""
    items = ChecklistItemWithProgressSerializer(many=True, read_only=True)

    class Meta:
        model = ChecklistCategory
        fields = ["id", "name", "description", "order", "icon", "items"]


class UserChecklistProgressSerializer(serializers.ModelSerializer):
    """
    Used to create/update a progress record.
    POST /api/v1/checklist/progress/ with { "item": <id>, "completed": true }
    """
    class Meta:
        model = UserChecklistProgress
        fields = ["id", "item", "completed", "completed_at"]
        read_only_fields = ["completed_at"]  # Set server-side when completed=True
