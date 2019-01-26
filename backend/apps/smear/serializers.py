from rest_framework import serializers

from apps.smear.models import Game, Player


class PlayerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'user', 'team')


class PlayerIDSerializer(serializers.Serializer):
    player_id = serializers.CharField(max_length=64)


class GameSerializer(serializers.ModelSerializer):
    passcode = serializers.CharField(write_only=True, required=False, allow_blank=True)
    status = serializers.SerializerMethodField()
    players = PlayerSummarySerializer(source='player_set', read_only=True, many=True)

    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = ('owner', 'passcode_required')

    def get_status(self, obj):
        return obj.get_status()


class GameJoinSerializer(serializers.Serializer):
    passcode = serializers.CharField(max_length=512, required=False)


class TeamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    player_ids = serializers.ListField(
        child=PlayerIDSerializer()
    )


class GameStartSerializer(serializers.Serializer):
    teams = serializers.ListField(
        child=TeamSerializer()
    )
