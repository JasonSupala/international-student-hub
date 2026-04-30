"""
directory/urls.py

Generated routes:
  GET /api/v1/directory/categories/
  GET /api/v1/directory/categories/<id>/
  GET /api/v1/directory/entries/
  GET /api/v1/directory/entries/<id>/
  GET /api/v1/directory/entries/map/   (custom action)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceCategoryViewSet, ServiceEntryViewSet

router = DefaultRouter()
router.register(r"categories", ServiceCategoryViewSet, basename="directory-category")
router.register(r"entries", ServiceEntryViewSet, basename="directory-entry")

urlpatterns = [
    path("", include(router.urls)),
]
