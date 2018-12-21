from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.smear.models import Game
from apps.smear.pagination import SmearPagination
from apps.smear.serializers import GameSerializer
from apps.smear.permissions import IsOwnerPermission


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
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsOwnerPermission]

        return super().get_permissions()

    def get_queryset(self):
        if self.request.query_params.get("public", "false") == "true":
            return Game.objects.all().exclude(owner=self.request.user).order_by('-created_at')
        else:
            return Game.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        passcode = serializer.validated_data.get('passcode', None)
        serializer.save(
            owner=self.request.user,
            passcode_required=(passcode and passcode != "")
        )

    def create(self, request):
        response = super().create(request)
        # Do stuff
        return response
