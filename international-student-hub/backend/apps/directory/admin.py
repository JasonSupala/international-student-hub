from django.contrib import admin
from .models import ServiceCategory, ServiceEntry


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]


@admin.register(ServiceEntry)
class ServiceEntryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "category", "university", "verified", "created_at"]
    list_filter = ["category", "verified", "university"]
    search_fields = ["name", "slug", "description", "detail_description", "tags", "address"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["verified"]  # Quick toggle verified status from list view
    ordering = ["-verified", "name"]
