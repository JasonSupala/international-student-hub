"""
bot/models.py — LINE Bot FAQ database.

BotFAQ stores trigger keywords and their canned responses.
The webhook handler queries this table to reply to LINE messages.
"""

from django.db import models


class BotFAQ(models.Model):
    """
    A single FAQ entry for the LINE Bot.

    How matching works:
      When a user sends a message to the LINE Bot, the webhook handler
      scans all active BotFAQ entries and checks if any trigger_keyword
      appears (case-insensitive) in the user's message.
      The first match wins and its response_text is sent back.

    Example:
      trigger_keyword: "arc"
      response_text: "To register your ARC, visit the NIA office at..."
    """

    # The keyword to look for in the user's message (case-insensitive match)
    trigger_keyword = models.CharField(
        max_length=100,
        unique=True,
        help_text="Single keyword or short phrase to match in user messages"
    )

    # The full response the bot will send back
    response_text = models.TextField(
        help_text="The response sent to the user. Keep under 1000 characters for LINE."
    )

    # Disable a FAQ entry without deleting it
    active = models.BooleanField(default=True)

    # Optional category for admin filtering
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional grouping: 'government', 'banking', 'housing', etc."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "✓" if self.active else "✗"
        return f"{status} [{self.trigger_keyword}]"

    class Meta:
        verbose_name = "Bot FAQ"
        verbose_name_plural = "Bot FAQs"
        ordering = ["trigger_keyword"]
