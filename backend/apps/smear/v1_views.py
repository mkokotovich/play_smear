import logging

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.smear.models import Game, Player
from apps.smear.pagination import SmearPagination
from apps.smear.serializers import (
    GameSerializer,
    GameJoinSerializer,
    GameStartSerializer,
    PlayerSummarySerializer,
    PlayerIDSerializer
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
        if self.request.query_params.get("public", "false") == "true":
            return Game.objects.filter(single_player=False).exclude(owner=self.request.user).order_by('-created_at')
        else:
            return Game.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        passcode = serializer.validated_data.get('passcode', None)
        instance = serializer.save(
            owner=self.request.user if self.request.user.is_authenticated else None,
            passcode_required=bool(passcode)
        )
        if self.request.user.is_authenticated:
            Player.objects.create(
                game=instance,
                user=self.request.user,
                is_computer=False
            )
        LOG.info(f"Created game {instance} and added {self.request.user} as player and creator")

        if instance.single_player:
            while instance.players.count() < instance.num_players:
                instance.add_computer_player()

        instance.save()

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def join(self, request, pk=None):
        game = Game.objects.get(id=pk)
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

        game = Game.objects.get(id=pk)
        game.start(serializer.validated_data)
        return Response({'status': 'success'})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsOwnerPermission],
    )
    def player(self, request, pk=None):
        if request.method == 'POST':
            game = Game.objects.get(id=pk)
            computer_player = game.add_computer_player()
            return Response({
                'status': 'success',
                'meta': {
                    'computer_player': PlayerSummarySerializer(computer_player).data,
                },
            })
        else:
            serializer = PlayerIDSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            player_id = serializer.validated_data['player_id']
            try:
                player = Player.objects.get(id=player_id)
            except Player.DoesNotExist:
                pass
            else:
                player.delete()
            return Response({
                'status': 'success',
            })
