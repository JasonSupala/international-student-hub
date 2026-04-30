from django.contrib import admin
from .models import BotFAQ


@admin.register(BotFAQ)
class BotFAQAdmin(admin.ModelAdmin):
    list_display = ["trigger_keyword", "category", "active", "updated_at"]
    list_filter = ["active", "category"]
    search_fields = ["trigger_keyword", "response_text"]
    list_editable = ["active"]
    ordering = ["trigger_keyword"]
