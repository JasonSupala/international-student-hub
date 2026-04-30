"""
directory/views.py
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ServiceCategory, ServiceEntry
from .serializers import (
    ServiceCategorySerializer,
    ServiceEntrySerializer,
    ServiceEntryMapSerializer,
)


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/directory/categories/       → all service categories
    GET /api/v1/directory/categories/<id>/  → single category
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]


class ServiceEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/directory/entries/                   → all verified entries
    GET /api/v1/directory/entries/<id>/              → single entry
    GET /api/v1/directory/entries/?category=<slug>   → filter by category
    GET /api/v1/directory/entries/?university=NSYSU  → filter by university
    GET /api/v1/directory/entries/?search=halal      → search name/description/tags

    Unverified entries are hidden by default (verified=True filter).
    """
    serializer_class = ServiceEntrySerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["category__slug", "university", "verified"]
    search_fields = ["name", "description", "tags", "address"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        qs = ServiceEntry.objects.select_related("category").filter(verified=True)

        # Allow staff to see unverified entries via ?verified=false
        show_unverified = self.request.query_params.get("show_unverified")
        if show_unverified and self.request.user.is_staff:
            qs = ServiceEntry.objects.select_related("category").all()

        return qs

    @action(detail=False, methods=["get"], url_path="map")
    def map_data(self, request):
        """
        GET /api/v1/directory/entries/map/
        Returns lightweight pin data for map display.
        Supports ?category=<slug>&university=<name> filters.
        """
        qs = self.get_queryset().exclude(latitude=None, longitude=None)

        category_slug = request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        university = request.query_params.get("university")
        if university:
            qs = qs.filter(university__in=[university, ""])

        serializer = ServiceEntryMapSerializer(qs, many=True)
        return Response(serializer.data)
