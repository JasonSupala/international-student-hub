"""
bot/urls.py

Routes:
  POST /api/v1/bot/webhook/   → LINE Messaging API webhook
  CRUD /api/v1/bot/faqs/      → Admin FAQ management (IsAdminUser only)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import line_webhook, BotFAQViewSet

router = DefaultRouter()
router.register(r"faqs", BotFAQViewSet, basename="bot-faq")

urlpatterns = [
    path("webhook/", line_webhook, name="line-webhook"),
    path("", include(router.urls)),
]
