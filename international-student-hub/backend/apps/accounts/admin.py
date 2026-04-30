from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Show the UserProfile fields directly on the User admin page."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register User with the extended admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
