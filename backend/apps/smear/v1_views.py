from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.smear.models import Game
from apps.smear.serializers import GameSerializer
from apps.smear.permissions import IsOwnerPermission


class GameViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    # search_fields = ('^client_number',)
    # filter_fields = ('test_type', 'client_number')
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
        if self.request.user.is_staff:
            return Game.objects.all().order_by('-created_at')
        else:
            return Game.objects.filter(owner=self.request.user).order_by('-created_at')

    # def perform_create(self, serializer):
        # serializer.save(owner=self.request.user)

    def create(self, request):
        response = super().create(request)
        # Do stuff
        return response
