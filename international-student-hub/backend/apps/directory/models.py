"""
directory/models.py — Searchable service directory.

Structure:
  ServiceCategory → type of service (food, clinic, bank, SIM, etc.)
  ServiceEntry    → a specific business/service students can visit
"""

from django.db import models


class ServiceCategory(models.Model):
    """
    Category for directory entries.
    Examples: "Food", "Clinics", "SIM Cards", "Banks", "Housing"
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="Used in URL filters, e.g. 'sim-cards'")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ["order"]


class ServiceEntry(models.Model):
    """
    A single business or service location in the directory.
    Examples: 7-Eleven near NSYSU (SIM), Kaohsiung Chang Gung Hospital (clinic)
    """
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="entries"
    )

    description = models.TextField(
        help_text="What makes this place useful for international students?"
    )

    # Physical location
    address = models.CharField(max_length=300)

    # Link to Google Maps (pre-built URL with pin)
    maps_link = models.URLField(
        blank=True,
        help_text="Full Google Maps URL for this location"
    )

    # For future map embed (Phase 2)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True
    )

    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    # Comma-separated tags for flexible filtering (e.g., "english-friendly,halal")
    tags = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated tags: english-friendly, halal, vegetarian, 24-hours"
    )

    # If set, only show for this university's students
    university = models.CharField(
        max_length=200,
        blank=True,
        help_text="Leave blank to show for all universities"
    )

    # Only show verified entries by default in the API
    verified = models.BooleanField(
        default=False,
        help_text="Verified entries are shown by default; unverified are flagged"
    )

    # Operating hours as free text (simple enough for MVP)
    hours = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. Mon-Fri 9am-6pm, Sat 10am-4pm"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        verbose_name_plural = "Service Entries"
        ordering = ["-verified", "name"]
