import logging

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.smear.models import Game
from apps.smear.pagination import SmearPagination
from apps.smear.serializers import GameSerializer
from apps.smear.permissions import IsOwnerPermission


LOG = logging.getLogger(__name__)


class GameViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    pagination_class = SmearPagination
    search_fields = ('name',)
    filter_fields = ('owner', 'passcode_required')
    serializer_class = GameSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsOwnerPermission]

        return super().get_permissions()

    def get_queryset(self):
        if self.request.query_params.get("public", "false") == "true":
            return Game.objects.all().exclude(owner=self.request.user).exclude(owner=None).order_by('-created_at')
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        game = Game.objects.get(id=pk)
        if game.num_joined >= game.num_players:
            raise ValidationError(f"Unable to join game, already contains {game.num_players} players")
        game.players.add(self.request.user)
        LOG.info(f"Added {self.request.user} to game {game}")
        game.save()
        return Response({'status': 'success'})
