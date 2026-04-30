"""
checklist/urls.py — DRF router generates all CRUD endpoints automatically.

Generated routes:
  GET  /api/v1/checklist/categories/
  GET  /api/v1/checklist/categories/<id>/
  GET  /api/v1/checklist/items/
  GET  /api/v1/checklist/items/<id>/
  GET  /api/v1/checklist/progress/
  POST /api/v1/checklist/progress/
  GET  /api/v1/checklist/progress/<id>/
  PATCH/PUT /api/v1/checklist/progress/<id>/
  DELETE    /api/v1/checklist/progress/<id>/
  GET  /api/v1/checklist/progress/summary/   (custom action)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChecklistCategoryViewSet, ChecklistItemViewSet, UserChecklistProgressViewSet

router = DefaultRouter()
router.register(r"categories", ChecklistCategoryViewSet, basename="checklist-category")
router.register(r"items", ChecklistItemViewSet, basename="checklist-item")
router.register(r"progress", UserChecklistProgressViewSet, basename="checklist-progress")

urlpatterns = [
    path("", include(router.urls)),
]
