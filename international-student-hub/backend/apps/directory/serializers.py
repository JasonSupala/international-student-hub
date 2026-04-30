"""
directory/serializers.py
"""

from rest_framework import serializers
from .models import ServiceCategory, ServiceEntry


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["id", "name", "slug", "description", "icon", "order"]


class ServiceEntrySerializer(serializers.ModelSerializer):
    # Include the category name as a read-only field alongside the ID
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ServiceEntry
        fields = [
            "id", "name", "category", "category_name",
            "description", "address", "maps_link",
            "latitude", "longitude",
            "phone", "website", "tags",
            "university", "verified", "hours",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ServiceEntryMapSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for the map endpoint — only fields needed to
    place pins on a map. Keeps the payload small.
    """
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ServiceEntry
        fields = [
            "id", "name", "category_name",
            "latitude", "longitude", "maps_link",
        ]
