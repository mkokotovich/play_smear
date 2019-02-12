import logging

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from apps.smear.models import Game, Player
from apps.smear.pagination import SmearPagination
from apps.smear.serializers import (
    GameSerializer,
    GameJoinSerializer,
    GameStartSerializer,
    PlayerSummarySerializer,
    PlayerIDSerializer,
    StatusStartingSerializer,
)
from apps.smear.permissions import IsOwnerPermission, IsPlayerInGame


LOG = logging.getLogger(__name__)


class GameViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    pagination_class = SmearPagination
    search_fields = ('name',)
    filter_fields = ('owner', 'passcode_required', 'single_player')
    serializer_class = GameSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwnerPermission]
        else:
            self.permission_classes = [IsPlayerInGame]

        return super().get_permissions()

    def get_queryset(self):
        base_queryset = (
            Game.objects.filter(single_player=False).exclude(owner=self.request.user) if
            self.request.query_params.get("public", "false") == "true" else
            Game.objects.all()
        )

        return base_queryset.order_by('-created_at')

    def perform_create(self, serializer):
        passcode = serializer.validated_data.get('passcode', None)
        instance = serializer.save(
            owner=self.request.user if self.request.user.is_authenticated else None,
            passcode_required=bool(passcode)
        )
        # TODO: allow unauthed single player games
        if self.request.user.is_authenticated:
            Player.objects.create(
                game=instance,
                user=self.request.user,
                is_computer=False
            )
        LOG.info(f"Created game {instance} and added {self.request.user} as player and creator")

        instance.create_initial_teams()

        if instance.single_player:
            while instance.players.count() < instance.num_players:
                instance.add_computer_player()

        instance.state = Game.STARTING

        instance.save()

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def join(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        serializer = GameJoinSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        if game.players.count() >= game.num_players:
            raise ValidationError(f"Unable to join game, already contains {game.num_players} players")
        if game.passcode_required and game.passcode != serializer.data.get('passcode', None):
            raise ValidationError(f"Unable to join game, passcode is required and was incorrect")

        Player.objects.create(game=game, user=self.request.user)
        LOG.info(f"Added {self.request.user} to game {game}")
        return Response({'status': 'success'})

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsOwnerPermission],
    )
    def start(self, request, pk=None):
        serializer = GameStartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        game = get_object_or_404(Game, pk=pk)
        game.start(serializer.validated_data)
        return Response({'status': 'success'})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsOwnerPermission],
    )
    def player(self, request, pk=None):
        if request.method == 'POST':
            game = get_object_or_404(Game, pk=pk)
            computer_player = game.add_computer_player()
            return Response(PlayerSummarySerializer(computer_player).data)
        else:
            serializer = PlayerIDSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            player_id = serializer.validated_data['id']
            try:
                player = Player.objects.get(id=player_id)
            except Player.DoesNotExist:
                pass
            else:
                player.delete()
            return Response({
                'status': 'success',
            })

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsPlayerInGame],
    )
    def status(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        serializer_class = {
            'starting': StatusStartingSerializer,
            'bidding': StatusStartingSerializer,
        }.get(game.state, None)
        if not serializer_class:
            raise APIException(f"Unable to find status of game {game}, state ({game.state}) is not supported")
        serializer = serializer_class(game)

        return Response(serializer.data)
