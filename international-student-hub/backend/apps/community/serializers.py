"""
community/serializers.py
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Post, Reply


class AuthorSerializer(serializers.ModelSerializer):
    """Minimal author info shown on posts and replies."""
    university = serializers.CharField(source="profile.university", read_only=True)
    country = serializers.CharField(source="profile.country", read_only=True)
    avatar = serializers.ImageField(source="profile.avatar", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "university", "country", "avatar"]


class ReplySerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = [
            "id", "post", "author", "body",
            "upvotes", "is_accepted", "created_at", "updated_at",
        ]
        read_only_fields = ["author", "upvotes", "created_at", "updated_at"]

    def create(self, validated_data):
        # Attach the current user as the author
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    reply_count = serializers.IntegerField(source="replies.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "author", "title", "body", "university",
            "upvotes", "reply_count", "created_at", "updated_at",
        ]
        read_only_fields = ["author", "upvotes", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class PostDetailSerializer(PostSerializer):
    """Post serializer with replies nested in. Used for the detail view."""
    replies = ReplySerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ["replies"]
