from django.contrib import admin
from .models import ChecklistCategory, ChecklistItem, UserChecklistProgress


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1
    fields = ["title", "slug", "order", "university", "is_active"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ChecklistCategory)
class ChecklistCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "icon"]
    inlines = [ChecklistItemInline]
    ordering = ["order"]


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "category", "university", "order", "is_active"]
    list_filter = ["category", "university", "is_active"]
    search_fields = ["title", "slug", "description", "detail_description"]
    prepopulated_fields = {"slug": ("title",)}
    ordering = ["category__order", "order"]


@admin.register(UserChecklistProgress)
class UserChecklistProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "item", "completed", "completed_at"]
    list_filter = ["completed"]
    search_fields = ["user__username", "item__title"]
