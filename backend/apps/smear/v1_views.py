import logging

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.smear.models import Game, Hand
from apps.smear.pagination import SmearPagination
from apps.smear.serializers import GameSerializer, GameJoinSerializer
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
            instance.players.add(self.request.user)
        LOG.info(f"Created game {instance} and added {self.request.user} as player and creator")
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

        game.players.add(self.request.user)
        LOG.info(f"Added {self.request.user} to game {game}")
        game.save()
        return Response({'status': 'success'})


    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsOwnerPermission],
    )
    def start(self, request, pk=None):
        game = Game.objects.get(id=pk)
        # serializer = GameJoinSerializer(data=request.data)
        # if not serializer.is_valid():
        #     return Response(
        #         serializer.errors,
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        if game.players.count() != game.num_players:
            raise ValidationError(f"Unable to start game, game requires {game.num_players} players, but {game.players.count()} have joined")

        hand = Hand(game=game)
        hand.save()
        LOG.info(f"Started hand {hand} on game {game}")
        return Response({'status': 'success'})
