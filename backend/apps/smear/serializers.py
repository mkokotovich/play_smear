from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.smear.models import Game, Team, Player, Hand, Bid


class PlayerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'user', 'team', 'is_computer')


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


class StatusStartingSerializer(serializers.ModelSerializer):
    teams = TeamSummarySerializer(read_only=True, many=True)
    players = PlayerSummarySerializer(source='player_set', read_only=True, many=True)

    class Meta:
        model = Game
        fields = ('teams', 'players', 'state')


class HandSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hand
        fields = ('id', 'dealer', 'bidder', 'high_bid')


class HandSummaryWithCardsSerializer(serializers.ModelSerializer):
    cards = serializers.SerializerMethodField('current_users_cards')

    def current_users_cards(self, obj):
        request = self.context.get('request', None)
        user = request.user if request else None
        if not user:
            return []
        try:
            player = obj.game.player_set.get(user=user)
        except Player.DoesNotExist:
            return []
        return player.cards_in_hand

    class Meta:
        model = Hand
        fields = ('id', 'dealer', 'bidder', 'high_bid', 'cards')


class StatusBiddingSerializer(serializers.ModelSerializer):
    current_hand = HandSummarySerializer(read_only=True)

    class Meta:
        model = Game
        fields = ('state', 'current_hand')


class GameSerializer(serializers.ModelSerializer):
    passcode = serializers.CharField(write_only=True, required=False, allow_blank=True)
    players = PlayerSummarySerializer(source='player_set', read_only=True, many=True)
    teams = TeamSummarySerializer(read_only=True, many=True)

    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = ('owner', 'passcode_required')


class GameDetailSerializer(GameSerializer):
    current_hand = HandSummaryWithCardsSerializer(read_only=True)


class GameJoinSerializer(serializers.Serializer):
    passcode = serializers.CharField(max_length=512, required=False)


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('id', 'bid')
        read_only_fields = ('player',)

    def validate_bid(self, value):
        hand = self.context['extra_kwargs'].get('hand')

        if value < 0 or value == 1 or value > 5:
            raise ValidationError(f"A bid of {value} is not a legal bid. Bids must be 0 (pass) or between 2 and 5")

        if value != 0 and hand.high_bid and hand.high_bid.bid >= value:
            raise ValidationError(f"Unable to bid {value}, there is already a bid of {hand.high_bid.bid}")

        return value
