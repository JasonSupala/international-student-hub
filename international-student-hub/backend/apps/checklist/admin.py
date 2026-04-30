from django.contrib import admin
from .models import ChecklistCategory, ChecklistItem, UserChecklistProgress


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1
    fields = ["title", "order", "university", "is_active"]


@admin.register(ChecklistCategory)
class ChecklistCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "icon"]
    inlines = [ChecklistItemInline]
    ordering = ["order"]


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "university", "order", "is_active"]
    list_filter = ["category", "university", "is_active"]
    search_fields = ["title", "description"]
    ordering = ["category__order", "order"]


@admin.register(UserChecklistProgress)
class UserChecklistProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "item", "completed", "completed_at"]
    list_filter = ["completed"]
    search_fields = ["user__username", "item__title"]
