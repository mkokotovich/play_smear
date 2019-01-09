from rest_framework import serializers

from apps.smear.models import Game


class GameSerializer(serializers.ModelSerializer):
    passcode = serializers.CharField(write_only=True, required=False, allow_blank=True)
    status = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = ('owner', 'passcode_required')

    def get_status(self, obj):
        return obj.get_status()

    def _get_username_from_player(self, player):
        name = player.first_name + f"{' ' + player.last_name[:1] if player.last_name else ''}"
        if not name:
            name = player.username.split('@')[0]
        return name

    def get_players(self, obj):
        return [{
            'id': player.id,
            'name': self._get_username_from_player(player),
            'team': '',
        } for player in obj.players.all()]


class GameJoinSerializer(serializers.Serializer):
    passcode = serializers.CharField(max_length=512, required=False)
