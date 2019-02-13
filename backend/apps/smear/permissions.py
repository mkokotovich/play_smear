from rest_framework import permissions

from apps.smear.models import Player


class IsOwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff


class IsPlayerInGame(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return Player.objects.filter(game_id=obj.id, user_id=request.user.id).exists() or obj.owner == request.user


class IsGameOwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.game.owner == request.user or request.user.is_staff


class IsPlayerOnTeam(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return Player.objects.filter(team_id=obj.id, user_id=request.user.id).exists() or obj.game.owner == request.user
