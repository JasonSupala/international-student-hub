"""
accounts/models.py — User profile extending Django's built-in User model.

We use a OneToOneField to extend User rather than a custom User model
because it's simpler to add without breaking Django's auth system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended profile for each registered user.
    Created automatically when a new User is saved (see signal below).
    """

    # Link to Django's built-in User (provides username, email, password, etc.)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # Where the student is from (e.g., "Indonesia", "Vietnam", "Japan")
    country = models.CharField(max_length=100, blank=True)

    # Which university they attend (e.g., "NSYSU", "NTU", "NCKU")
    university = models.CharField(max_length=200, blank=True)

    # When they arrived or plan to arrive in Taiwan
    arrival_date = models.DateField(null=True, blank=True)

    # Short personal bio visible in the community section
    bio = models.TextField(blank=True, max_length=500)

    # Profile picture (optional)
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True
    )

    # Preferred language for future multi-language support
    preferred_language = models.CharField(
        max_length=10,
        default="en",
        choices=[
            ("en", "English"),
            ("id", "Bahasa Indonesia"),
            ("vi", "Vietnamese"),
            ("ja", "Japanese"),
            ("zh", "Traditional Chinese"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.university or 'No university set'}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# --------------------------------------------------------------------------
# Signal: Auto-create UserProfile when a new User is registered
# --------------------------------------------------------------------------

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a new User account is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Keep the UserProfile in sync when the User is saved."""
    # hasattr check handles cases where User exists without a profile (e.g., superuser created via CLI)
    if hasattr(instance, "profile"):
        instance.profile.save()
