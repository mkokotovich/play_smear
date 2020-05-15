import logging

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.smear.models import Game, Player, Team, Bid, Hand, Trick, Play
from apps.smear.pagination import SmearPagination
from apps.smear.serializers import (
    GameSerializer,
    GameDetailSerializer,
    GameJoinSerializer,
    PlayerSummarySerializer,
    PlayerIDSerializer,
    StatusStartingSerializer,
    StatusBiddingSerializer,
    StatusPlayingTrickSerializer,
    TeamSummarySerializer,
    TeamSerializer,
    BidSerializer,
    PlaySerializer,
)
from apps.smear.permissions import IsPlayerInGame, IsGameOwnerPermission, IsPlayerOnTeam, IsBidOwnerPermission


LOG = logging.getLogger(__name__)


class GameViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    pagination_class = SmearPagination
    search_fields = ('name',)
    filterset_fields = ('owner', 'passcode_required', 'single_player')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GameDetailSerializer
        else:
            return GameSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            self.permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsGameOwnerPermission]

        return super().get_permissions()

    def get_queryset(self):
        base_queryset = (
            Game.objects.filter(single_player=False).exclude(owner=self.request.user) if
            self.request.query_params.get("public", "false") == "true" else
            Game.objects.all()
        )

        return base_queryset.order_by('-id')

    @transaction.atomic
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
        game = self.get_object()
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
        permission_classes=[IsGameOwnerPermission],
    )
    def start(self, request, pk=None):
        game = self.get_object()
        game.start_game()
        LOG.info(f"Started game {game}")
        return Response({'status': 'success'})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsGameOwnerPermission],
    )
    def player(self, request, pk=None):
        game = self.get_object()
        if request.method == 'POST':
            computer_player = game.add_computer_player()
            LOG.info(f"Added computer {computer_player} to game {game}")
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
                LOG.info(f"Player with ID {player_id} did not exist")
                pass
            else:
                player.delete()
                LOG.info(f"Removed {player} from game {pk}")
            return Response({
                'status': 'success',
            })

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsPlayerInGame],
    )
    def status(self, request, pk=None):
        game = self.get_object()
        status_serializer = {
            Game.STARTING: StatusStartingSerializer,
            Game.BIDDING: StatusBiddingSerializer,
            Game.DECLARING_TRUMP: StatusBiddingSerializer,
            Game.PLAYING_TRICK: StatusPlayingTrickSerializer,
        }.get(game.state, None)
        if not status_serializer:
            raise APIException(f"Unable to find status of game {game}, state ({game.state}) is not supported")

        context = {
            **self.get_serializer_context(),
            'trick_num': request.query_params.get('trick_num'),
            'hand_num': request.query_params.get('hand_num'),
        }
        serializer = status_serializer(game, context=context)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsPlayerInGame],
    )
    def auto_pilot(self, request, pk=None):
        game = self.get_object()
        player = Player.objects.get(game=game, user=self.request.user)
        LOG.info(f"Setting player {player} to auto-pilot {'disabled' if player.is_computer else 'enabled'}")
        player.is_computer = not player.is_computer
        player.save()
        return Response({'status': 'success'})


class TeamViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    pagination_class = SmearPagination
    serializer_class = TeamSummarySerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update']:
            self.permission_classes = [IsGameOwnerPermission]
        elif self.action in ['list', 'retrieve', 'partial_update']:
            self.permission_classes = [IsPlayerOnTeam]

        return super().get_permissions()

    def get_queryset(self):
        game_id = self.kwargs.get('game_id')
        return Team.objects.filter(game_id=game_id).select_related('game').order_by('-id')

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsGameOwnerPermission],
    )
    def member(self, request, pk=None, game_id=None):
        team = self.get_object()
        serializer = PlayerIDSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        player_id = serializer.validated_data['id']
        player = get_object_or_404(Player, pk=player_id)

        adding = request.method == 'POST'

        player.team = team if adding else None
        player.save()
        LOG.info(f"{'Added' if adding else 'Removed'} player {player} {'to' if adding else 'from'} team {team}")

        return Response(TeamSerializer(team).data)

    @action(
        detail=False,
        methods=['post', 'delete'],
        permission_classes=[IsGameOwnerPermission],
    )
    def all(self, request, game_id=None):
        game = get_object_or_404(Game, pk=game_id)

        if request.method == 'POST':
            LOG.info(f"Autofilling teams for game {game}")
            game.autofill_teams()

        elif request.method == 'DELETE':
            LOG.info(f"Resetting teams for game {game}")
            game.reset_teams()

        game.save()

        return Response(GameSerializer(game).data)


class BidViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    pagination_class = SmearPagination
    serializer_class = BidSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            self.permission_classes = [IsPlayerInGame]
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsBidOwnerPermission]

        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        player = Player.objects.get(game=self.kwargs['game_id'], user=self.request.user)
        hand = Hand.objects.get(pk=self.kwargs['hand_id'])
        context['extra_kwargs'] = {
            'hand': hand,
            'player': player,
        }
        return context

    def get_queryset(self):
        game_id = self.kwargs.get('game_id')
        hand_id = self.kwargs.get('hand_id')
        return Bid.objects.filter(hand__game_id=game_id, hand_id=hand_id).select_related('hand__game').order_by('-id')

    @transaction.atomic
    def perform_create(self, serializer):
        bid = serializer.save(**serializer.context['extra_kwargs'])
        bid.hand.submit_bid(bid)
        return bid

    def perform_update(self, serializer):
        hand = serializer.context['extra_kwargs'].get('hand')
        player = serializer.context['extra_kwargs'].get('player')

        if hand.game.state == Game.BIDDING:
            if not hand.player_can_change_bid(player):
                raise ValidationError("No longer able to change bid")
        elif hand.game.state == Game.DECLARING_TRUMP:
            if player != hand.high_bid.player:
                raise ValidationError("Not able to change bid after bidder is chosen")
            bid = serializer.validated_data.get('bid', None)
            if bid and bid != self.get_object().bid:
                raise ValidationError("Changing the bid is not allowed while declaring trump")
        else:
            raise ValidationError("No longer able to change bid")

        bid = serializer.save(**serializer.context['extra_kwargs'])

        if hand.game.state == Game.DECLARING_TRUMP and bid.trump:
            hand.finalize_trump_declaration(bid.trump)


class PlayViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    pagination_class = SmearPagination
    serializer_class = PlaySerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            self.permission_classes = [IsPlayerInGame]
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsPlayOwnerPermission]

        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        player = Player.objects.get(game=self.kwargs['game_id'], user=self.request.user)
        trick = Trick.objects.get(pk=self.kwargs['trick_id'])
        context['extra_kwargs'] = {
            'player': player,
            'trick': trick,
        }
        return context

    def get_queryset(self):
        trick_id = self.kwargs.get('trick_id')
        return Play.objects.filter(trick_id=trick_id).select_related('trick__hand__game').order_by('-id')

    @transaction.atomic
    def perform_create(self, serializer):
        play = serializer.save(**serializer.context['extra_kwargs'])
        trick = serializer.context['extra_kwargs'].get('trick')
        trick.submit_play(play)
        return play

    def perform_update(self, serializer):
        trick = serializer.context['extra_kwargs'].get('trick')
        player = serializer.context['extra_kwargs'].get('player')

        if not trick.player_can_change_play(player):
            raise ValidationError("No longer able to change card to play")

        play = serializer.save(**serializer.context['extra_kwargs'])
        return play
