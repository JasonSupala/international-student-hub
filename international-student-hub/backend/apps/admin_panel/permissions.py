from rest_framework.permissions import IsAdminUser


class IsSuperuser(IsAdminUser):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and bool(request.user and request.user.is_superuser)
        )
