from rest_framework.routers import DefaultRouter

from .views import (
    BotFAQViewSet,
    ChecklistCategoryViewSet,
    ChecklistItemViewSet,
    PostViewSet,
    ReplyViewSet,
    ServiceCategoryViewSet,
    ServiceEntryViewSet,
    UserChecklistProgressViewSet,
    UserProfileViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="admin-users")
router.register("user-profiles", UserProfileViewSet, basename="admin-user-profiles")
router.register("checklist-categories", ChecklistCategoryViewSet, basename="admin-checklist-categories")
router.register("checklist-items", ChecklistItemViewSet, basename="admin-checklist-items")
router.register("checklist-progress", UserChecklistProgressViewSet, basename="admin-checklist-progress")
router.register("service-categories", ServiceCategoryViewSet, basename="admin-service-categories")
router.register("service-entries", ServiceEntryViewSet, basename="admin-service-entries")
router.register("posts", PostViewSet, basename="admin-posts")
router.register("replies", ReplyViewSet, basename="admin-replies")
router.register("bot-faqs", BotFAQViewSet, basename="admin-bot-faqs")

urlpatterns = router.urls
