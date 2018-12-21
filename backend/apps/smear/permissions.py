from rest_framework import permissions


class IsOwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff