"""
checklist/views.py
"""

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import ChecklistCategory, ChecklistItem, UserChecklistProgress
from .serializers import (
    ChecklistCategorySerializer,
    ChecklistItemWithProgressSerializer,
    UserChecklistProgressSerializer,
)


class ChecklistCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/checklist/categories/         → all categories with items
    GET /api/v1/checklist/categories/<id>/    → single category with items

    ReadOnly because categories are managed by admins, not users.
    Items have per-user progress injected by the serializer.
    """
    queryset = ChecklistCategory.objects.prefetch_related("items").all()
    serializer_class = ChecklistCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        # Optional: filter by university via ?university=NSYSU
        university = self.request.query_params.get("university")
        if university:
            # Include items for this university AND items with no university restriction
            qs = qs.filter(
                items__university__in=[university, ""]
            ).distinct()
        return qs


class ChecklistItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/checklist/items/          → all active items
    GET /api/v1/checklist/items/<id>/     → single item with user progress

    Supports filtering: ?category=<id>&university=NSYSU
    """
    queryset = ChecklistItem.objects.filter(is_active=True).select_related("category")
    serializer_class = ChecklistItemWithProgressSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["category", "university"]
    search_fields = ["title", "description"]

    def get_serializer_context(self):
        # Pass request to serializer so it can look up per-user progress
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class UserChecklistProgressViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/checklist/progress/        → current user's progress records
    POST   /api/v1/checklist/progress/        → mark an item (body: {item, completed})
    PATCH  /api/v1/checklist/progress/<id>/   → update a progress record
    DELETE /api/v1/checklist/progress/<id>/   → unmark (or just PATCH completed=false)

    All operations are scoped to the currently authenticated user.
    """
    serializer_class = UserChecklistProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own progress
        return UserChecklistProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        On creation, use get_or_create so re-marking an item doesn't error.
        Set completed_at when completed=True.
        """
        completed = serializer.validated_data.get("completed", False)
        progress, created = UserChecklistProgress.objects.get_or_create(
            user=self.request.user,
            item=serializer.validated_data["item"],
            defaults={
                "completed": completed,
                "completed_at": timezone.now() if completed else None,
            },
        )
        if not created:
            # Record already exists — update it
            progress.completed = completed
            progress.completed_at = timezone.now() if completed else None
            progress.save()

    def perform_update(self, serializer):
        """Auto-set completed_at when a record is marked complete."""
        instance = serializer.save()
        if instance.completed and not instance.completed_at:
            instance.completed_at = timezone.now()
            instance.save()

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        GET /api/v1/checklist/progress/summary/
        Returns: { total_items, completed_count, percent_complete }
        Useful for a progress bar on the frontend.
        """
        total = ChecklistItem.objects.filter(is_active=True).count()
        completed = UserChecklistProgress.objects.filter(
            user=request.user, completed=True
        ).count()
        percent = round((completed / total * 100), 1) if total > 0 else 0

        return Response({
            "total_items": total,
            "completed_count": completed,
            "percent_complete": percent,
        })
