"""
checklist/models.py — Arrival checklist system.

Structure:
  ChecklistCategory → groups related items (e.g., "Government", "Banking")
  ChecklistItem     → a single task the student needs to complete
  UserChecklistProgress → tracks which items each user has completed
"""

from django.db import models
from django.contrib.auth.models import User


class ChecklistCategory(models.Model):
    """
    Top-level grouping for checklist items.
    Examples: "Government Registration", "Banking", "SIM Card", "Housing"
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Controls display order on the frontend
    order = models.PositiveIntegerField(default=0)

    # Emoji icon for visual display (e.g., "🏛️", "💳")
    icon = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Checklist Categories"
        ordering = ["order"]


class ChecklistItem(models.Model):
    """
    A single task in the arrival checklist.
    Items can be university-specific or apply to all universities.
    """
    category = models.ForeignKey(
        ChecklistCategory,
        on_delete=models.CASCADE,
        related_name="items"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(
        help_text="Detailed instructions for completing this task"
    )

    # Order within the category
    order = models.PositiveIntegerField(default=0)

    # Optional: link to an external resource (e.g., NIA website for ARC)
    resource_url = models.URLField(blank=True)

    # If set, this item only appears for students at this university.
    # If blank, it applies to all universities.
    university = models.CharField(
        max_length=200,
        blank=True,
        help_text="Leave blank to show for all universities"
    )

    # Estimated time to complete (in minutes)
    estimated_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated time to complete this task in minutes"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category.name}] {self.title}"

    class Meta:
        ordering = ["category__order", "order"]


class UserChecklistProgress(models.Model):
    """
    Tracks which checklist items a specific user has completed.
    One row per user per item — created on-demand when a user marks an item.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="checklist_progress"
    )
    item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE,
        related_name="user_progress"
    )
    completed = models.BooleanField(default=False)

    # Timestamp when the user marked this complete (null if not yet done)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Each user can only have one progress record per item
        unique_together = ("user", "item")
        verbose_name_plural = "User Checklist Progress"

    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.user.username} — {self.item.title}"
