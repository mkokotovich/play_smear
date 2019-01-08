from rest_framework import permissions


class IsOwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff


class IsPlayerInGame(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.players.filter(id=request.user.id).exists()
