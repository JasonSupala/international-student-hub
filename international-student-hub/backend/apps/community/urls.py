"""
community/urls.py

Generated routes:
  GET/POST        /api/v1/community/posts/
  GET/PATCH/DELETE /api/v1/community/posts/<id>/
  POST            /api/v1/community/posts/<id>/upvote/
  GET/POST        /api/v1/community/replies/
  GET/PATCH/DELETE /api/v1/community/replies/<id>/
  POST            /api/v1/community/replies/<id>/upvote/
  POST            /api/v1/community/replies/<id>/accept/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, ReplyViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="community-post")
router.register(r"replies", ReplyViewSet, basename="community-reply")

urlpatterns = [
    path("", include(router.urls)),
]
