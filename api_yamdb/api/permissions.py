from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'moderator' or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser
            )
        )


class ReviewsAndCommentsPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or (
            request.user.is_authenticated
        ):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or (
            request.user.role in ('admin', 'moderator') or (
                request.user.is_superuser
            )
        )
