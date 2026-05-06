from django.contrib.auth.models import User
from rest_framework import viewsets

from apps.accounts.models import UserProfile
from apps.bot.models import BotFAQ
from apps.checklist.models import ChecklistCategory, ChecklistItem, UserChecklistProgress
from apps.community.models import Post, Reply
from apps.directory.models import ServiceCategory, ServiceEntry

from .permissions import IsSuperuser
from .serializers import (
    AdminBotFAQSerializer,
    AdminChecklistCategorySerializer,
    AdminChecklistItemSerializer,
    AdminPostSerializer,
    AdminReplySerializer,
    AdminServiceCategorySerializer,
    AdminServiceEntrySerializer,
    AdminUserChecklistProgressSerializer,
    AdminUserProfileSerializer,
    AdminUserSerializer,
)


class AdminModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperuser]


class UserViewSet(AdminModelViewSet):
    queryset = User.objects.select_related("profile").order_by("id")
    serializer_class = AdminUserSerializer
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "email", "date_joined", "last_login"]


class UserProfileViewSet(AdminModelViewSet):
    queryset = UserProfile.objects.select_related("user").order_by("id")
    serializer_class = AdminUserProfileSerializer
    search_fields = ["user__username", "country", "university", "bio"]
    ordering_fields = ["id", "created_at", "updated_at"]


class ChecklistCategoryViewSet(AdminModelViewSet):
    queryset = ChecklistCategory.objects.all()
    serializer_class = AdminChecklistCategorySerializer
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "order"]


class ChecklistItemViewSet(AdminModelViewSet):
    queryset = ChecklistItem.objects.select_related("category").all()
    serializer_class = AdminChecklistItemSerializer
    search_fields = ["title", "slug", "description", "detail_description", "university"]
    ordering_fields = ["id", "title", "order", "created_at"]


class UserChecklistProgressViewSet(AdminModelViewSet):
    queryset = UserChecklistProgress.objects.select_related("user", "item").order_by("id")
    serializer_class = AdminUserChecklistProgressSerializer
    search_fields = ["user__username", "item__title"]
    ordering_fields = ["id", "completed", "completed_at"]


class ServiceCategoryViewSet(AdminModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = AdminServiceCategorySerializer
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["id", "name", "order"]


class ServiceEntryViewSet(AdminModelViewSet):
    queryset = ServiceEntry.objects.select_related("category").all()
    serializer_class = AdminServiceEntrySerializer
    search_fields = [
        "name", "slug", "description", "detail_description",
        "address", "tags", "university",
    ]
    ordering_fields = ["id", "name", "verified", "created_at", "updated_at"]


class PostViewSet(AdminModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("upvoted_by").all()
    serializer_class = AdminPostSerializer
    search_fields = ["title", "body", "university", "author__username"]
    ordering_fields = ["id", "title", "upvotes", "created_at", "updated_at"]


class ReplyViewSet(AdminModelViewSet):
    queryset = Reply.objects.select_related("post", "author").prefetch_related("upvoted_by").all()
    serializer_class = AdminReplySerializer
    search_fields = ["body", "post__title", "author__username"]
    ordering_fields = ["id", "upvotes", "is_accepted", "created_at", "updated_at"]


class BotFAQViewSet(AdminModelViewSet):
    queryset = BotFAQ.objects.all()
    serializer_class = AdminBotFAQSerializer
    search_fields = ["trigger_keyword", "response_text", "category"]
    ordering_fields = ["id", "trigger_keyword", "active", "created_at", "updated_at"]
