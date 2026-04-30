"""
community/views.py
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, Reply
from .serializers import PostSerializer, PostDetailSerializer, ReplySerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only the author of a post/reply can edit or delete it.
    Everyone else gets read-only access.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/community/posts/         → list all posts
    POST   /api/v1/community/posts/         → create a post (auth required)
    GET    /api/v1/community/posts/<id>/    → retrieve post with replies
    PATCH  /api/v1/community/posts/<id>/    → update own post
    DELETE /api/v1/community/posts/<id>/    → delete own post

    Filter by ?university=NSYSU
    Search by ?search=banking
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filterset_fields = ["university"]
    search_fields = ["title", "body"]
    ordering_fields = ["created_at", "upvotes"]

    def get_queryset(self):
        # Hide soft-deleted posts
        return Post.objects.filter(is_hidden=False).select_related("author__profile")

    def get_serializer_class(self):
        # Use the detail serializer (with replies) for retrieve action
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, pk=None):
        """
        POST /api/v1/community/posts/<id>/upvote/
        Increment upvote count. Simple integer bump for MVP.
        """
        post = self.get_object()
        user = request.user
        if user in post.upvoted_by.all():
            return Response(
                {"error": "You have already upvoted this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        post.upvoted_by.add(user)
        post.upvotes += 1
        post.save()
        return Response({"upvotes": post.upvotes})


class ReplyViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/community/replies/?post=<id>   → replies for a post
    POST   /api/v1/community/replies/              → create a reply
    PATCH  /api/v1/community/replies/<id>/         → edit own reply
    DELETE /api/v1/community/replies/<id>/         → delete own reply
    """
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filterset_fields = ["post"]

    def get_queryset(self):
        return Reply.objects.select_related("author__profile", "post")

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, pk=None):
        """POST /api/v1/community/replies/<id>/upvote/"""
        reply = self.get_object()
        user = request.user
        if user in reply.upvoted_by.all():
            return Response(
                {"error": "You have already upvoted this reply."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reply.upvoted_by.add(user)
        reply.upvotes += 1
        reply.save()
        return Response({"upvotes": reply.upvotes})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        """
        POST /api/v1/community/replies/<id>/accept/
        Mark this reply as the accepted answer.
        Only the post author can do this.
        """
        reply = self.get_object()
        if reply.post.author != request.user:
            return Response(
                {"error": "Only the post author can accept an answer."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Un-accept any other accepted replies on this post first
        reply.post.replies.filter(is_accepted=True).update(is_accepted=False)
        reply.is_accepted = True
        reply.save()
        return Response({"is_accepted": True})
