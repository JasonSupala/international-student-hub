from django.contrib import admin
from .models import Post, Reply


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0
    fields = ["author", "body", "upvotes", "is_accepted"]
    readonly_fields = ["author", "upvotes"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "university", "upvotes", "is_hidden", "created_at"]
    list_filter = ["university", "is_hidden"]
    search_fields = ["title", "body", "author__username"]
    list_editable = ["is_hidden"]
    inlines = [ReplyInline]


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "upvotes", "is_accepted", "created_at"]
    list_filter = ["is_accepted"]
    search_fields = ["body", "author__username"]
