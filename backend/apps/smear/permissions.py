from rest_framework import permissions

from apps.smear.models import Player, Game, Team, Bid


class IsPlayerInGame(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Game):
            game = obj
        elif isinstance(obj, Team):
            game = obj.game
        elif isinstance(obj, Bid):
            game = obj.hand.game
        return Player.objects.filter(game_id=game.id, user_id=request.user.id).exists() or game.owner == request.user


class IsGameOwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Game):
            game = obj
        elif isinstance(obj, Team):
            game = obj.game
        elif isinstance(obj, Bid):
            game = obj.hand.game
        return game.owner == request.user or request.user.is_staff


class IsPlayerOnTeam(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        team = obj
        return Player.objects.filter(team_id=team.id, user_id=request.user.id).exists() or team.game.owner == request.user


class IsBidOwnerPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        bid = obj
        return bid.player.user == request.user
