from django.contrib import admin
from .models import ServiceCategory, ServiceEntry


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]


@admin.register(ServiceEntry)
class ServiceEntryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "university", "verified", "created_at"]
    list_filter = ["category", "verified", "university"]
    search_fields = ["name", "description", "tags", "address"]
    list_editable = ["verified"]  # Quick toggle verified status from list view
    ordering = ["-verified", "name"]
