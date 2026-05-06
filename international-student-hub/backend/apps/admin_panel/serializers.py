from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import UserProfile
from apps.bot.models import BotFAQ
from apps.checklist.models import ChecklistCategory, ChecklistItem, UserChecklistProgress
from apps.community.models import Post, Reply
from apps.directory.models import ServiceCategory, ServiceEntry


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    profile_id = serializers.IntegerField(source="profile.id", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "is_active", "is_staff", "is_superuser", "password",
            "profile_id", "last_login", "date_joined",
        ]
        read_only_fields = ["id", "profile_id", "last_login", "date_joined"]

    def validate_password(self, value):
        if value:
            validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", "")
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", "")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AdminUserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id", "user", "username", "country", "university", "arrival_date",
            "bio", "avatar", "preferred_language", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "username", "avatar", "created_at", "updated_at"]


class AdminChecklistCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistCategory
        fields = ["id", "name", "description", "order", "icon"]
        read_only_fields = ["id"]


class AdminChecklistItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ChecklistItem
        fields = [
            "id", "category", "category_name", "title", "slug", "description",
            "detail_description", "order", "resource_url", "university",
            "estimated_minutes", "is_active", "created_at",
        ]
        read_only_fields = ["id", "category_name", "created_at"]


class AdminUserChecklistProgressSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    item_title = serializers.CharField(source="item.title", read_only=True)

    class Meta:
        model = UserChecklistProgress
        fields = [
            "id", "user", "username", "item", "item_title",
            "completed", "completed_at",
        ]
        read_only_fields = ["id", "username", "item_title"]


class AdminServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["id", "name", "slug", "description", "icon", "order"]
        read_only_fields = ["id"]


class AdminServiceEntrySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ServiceEntry
        fields = [
            "id", "name", "slug", "category", "category_name",
            "description", "detail_description", "address", "maps_link",
            "latitude", "longitude", "phone", "website", "tags",
            "university", "verified", "hours", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "category_name", "created_at", "updated_at"]


class AdminPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    upvoted_by = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Post
        fields = [
            "id", "author", "author_username", "title", "body", "university",
            "upvotes", "upvoted_by", "is_hidden", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author_username", "created_at", "updated_at"]


class AdminReplySerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    post_title = serializers.CharField(source="post.title", read_only=True)
    upvoted_by = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Reply
        fields = [
            "id", "post", "post_title", "author", "author_username", "body",
            "upvotes", "upvoted_by", "is_accepted", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "post_title", "author_username", "created_at", "updated_at"]


class AdminBotFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotFAQ
        fields = [
            "id", "trigger_keyword", "response_text",
            "active", "category", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
