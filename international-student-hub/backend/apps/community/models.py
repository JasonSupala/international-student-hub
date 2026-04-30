"""
community/models.py — Community Q&A board.

Structure:
  Post  → a question or discussion thread
  Reply → a response to a Post
"""

from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """
    A community question or discussion post.
    Similar to a Reddit thread or Stack Overflow question.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # Keep post if user deletes their account
        null=True,
        related_name="posts"
    )

    title = models.CharField(max_length=300)
    body = models.TextField()

    # Helps filter posts by university (or show all with blank)
    university = models.CharField(
        max_length=200,
        blank=True,
        help_text="Leave blank for Taiwan-wide questions"
    )

    # Upvote count stored as an integer for simplicity in MVP.
    # Phase 2: replace with a PostVote model for user-specific voting.
    upvotes = models.PositiveIntegerField(default=0)
    upvoted_by = models.ManyToManyField(User, related_name="upvoted_posts", blank=True)

    # Soft-delete: hide post without destroying data
    is_hidden = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class Reply(models.Model):
    """
    A reply to a community Post.
    Replies are flat (no threading in MVP).
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="replies"
    )

    body = models.TextField()
    upvotes = models.PositiveIntegerField(default=0)
    upvoted_by = models.ManyToManyField(User, related_name="upvoted_replies", blank=True)

    # Mark the best answer (post author can mark one reply as accepted)
    is_accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reply by {self.author} on '{self.post.title}'"

    class Meta:
        ordering = ["-is_accepted", "-upvotes", "created_at"]
        verbose_name_plural = "Replies"
