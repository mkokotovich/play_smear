from rest_framework import permissions

from apps.smear.models import Bid, Game, Play, Player, Spectator, Team


class IsPlayerInGame(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.detail is True:
            # Allow this case to go to has_object_permissions
            return True
        game_id = view.kwargs.get("game_id", None)
        if not game_id:
            return False
        user_id = request.user.id
        return (
            Player.objects.filter(game_id=game_id, user_id=user_id).exists()
            or Spectator.objects.filter(game_id=game_id, user_id=user_id).exists()
        )

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Game):
            game_id = obj.id
        elif isinstance(obj, Team):
            game_id = obj.game_id
        elif isinstance(obj, Bid):
            game_id = obj.hand.game_id
        elif isinstance(obj, Play):
            game_id = obj.trick.hand.game_id
        user_id = request.user.id
        return (
            Player.objects.filter(game_id=game_id, user_id=user_id).exists()
            or Spectator.objects.filter(game_id=game_id, user_id=user_id).exists()
        )


class IsGameOwnerPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.detail is True:
            # Allow this case to go to has_object_permissions
            return True
        game_id = view.kwargs.get("game_id", None)
        if not game_id:
            return False
        game = Game.objects.get(pk=game_id)
        return game.owner == request.user or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Game):
            game = obj
        elif isinstance(obj, Team):
            game = obj.game
        elif isinstance(obj, Bid):
            game = obj.hand.game
        return game.owner == request.user or request.user.is_staff


class IsPlayerOnTeam(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.detail is True:
            # Allow this case to go to has_object_permissions
            return True
        return False

    def has_object_permission(self, request, view, obj):
        team = obj
        return (
            Player.objects.filter(team_id=team.id, user_id=request.user.id).exists() or team.game.owner == request.user
        )


class IsBidOwnerPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.detail is True:
            # Allow this case to go to has_object_permissions
            return True
        return False

    def has_object_permission(self, request, view, obj):
        bid = obj
        return bid.player.user == request.user


class IsPlayOwnerPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.detail is True:
            # Allow this case to go to has_object_permissions
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return obj.player.user == request.user
