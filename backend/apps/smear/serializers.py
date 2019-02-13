from rest_framework import serializers

from apps.smear.models import Game, Team, Player


class PlayerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'user', 'team')


class PlayerIDSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'members')


class TeamSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')


class GameSerializer(serializers.ModelSerializer):
    passcode = serializers.CharField(write_only=True, required=False, allow_blank=True)
    players = PlayerSummarySerializer(source='player_set', read_only=True, many=True)
    teams = TeamSummarySerializer(read_only=True, many=True)

    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = ('owner', 'passcode_required')


class GameJoinSerializer(serializers.Serializer):
    passcode = serializers.CharField(max_length=512, required=False)


class StatusStartingSerializer(serializers.ModelSerializer):
    teams = TeamSummarySerializer()
    players = PlayerSummarySerializer()

    class Meta:
        model = Game
        fields = '__none__'
