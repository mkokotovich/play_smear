import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.smear.cards import SUITS, Card
from apps.smear.models import Bid, Game, Hand, Play, Player, Team, Trick

LOG = logging.getLogger(__name__)


def sort_by_seat_if_present(players_unsorted):
    def key_finder(player):
        return player.seat if player.seat else 0
    return sorted(players_unsorted, key=key_finder)


class PlayerSummarySerializer(serializers.ModelSerializer):
    game_points_won = serializers.SerializerMethodField()

    def get_game_points_won(self, player):
        player_id = str(player.id)
        gpbp = self.context.get("game_points_by_player", {})
        return gpbp.get(player_id, 0)

    class Meta:
        model = Player
        fields = (
            "id",
            "name",
            "user",
            "team",
            "is_computer",
            "score",
            "winner",
            "seat",
            "game_points_won",
        )


class PlayerIDSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "members", "score", "winner", "color")


class TeamSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "score", "winner", "color")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "card", "player")
        read_only_fields = ("player",)

    def validate_card(self, value):
        try:
            trick = self.context["extra_kwargs"]["trick"]
            player = self.context["extra_kwargs"]["player"]
        except KeyError:
            raise ValidationError("context not set up correctly, extra_kwargs needs to contain trick and player")
        try:
            card = Card(representation=value)
        except ValueError as ex:
            raise ValidationError("invalid card, use short representation") from ex

        lead_play = trick.get_lead_play()
        error_msg = trick.is_card_invalid_to_play(card, player, lead_play)
        if error_msg:
            raise ValidationError(f"Unable to play {card.pretty} ({error_msg}), please choose another card")

        return value


class StatusStartingSerializer(serializers.ModelSerializer):
    teams = TeamSummarySerializer(read_only=True, many=True)
    players = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ("teams", "players", "state")

    def get_players(self, game):
        # Ordering by seat invalidates our prefetch_related, so we'll order in the app
        players_unsorted = game.player_set.all()
        players = sort_by_seat_if_present(players_unsorted)
        return PlayerSummarySerializer(players, many=True, read_only=True, context=self.context).data


class HandSummarySerializer(serializers.ModelSerializer):
    bids = serializers.SerializerMethodField()

    class Meta:
        model = Hand
        fields = ("id", "num", "dealer", "bidder", "high_bid", "trump", "bids", "finished")

    def get_bids(self, hand):
        return BidSerializer(hand.bids.all(), many=True, read_only=True, context=self.context).data if hand else []


class HandSummaryWithCardsSerializer(HandSummarySerializer):
    cards = serializers.SerializerMethodField("current_users_cards")
    results = serializers.SerializerMethodField()

    def current_users_cards(self, obj):
        request = self.context.get("request", None)
        user = request.user if request else None
        if not user:
            return []
        try:
            player = obj.game.player_set.get(user=user)
        except Player.DoesNotExist:
            return []
        return player.cards_in_hand

    def get_results(self, hand):
        return (
            {
                "winner_high": hand.winner_high.id if hand.winner_high else None,
                "winner_low": hand.winner_low.id if hand.winner_low else None,
                "winner_jick": hand.winner_jick.id if hand.winner_jick else None,
                "winner_jack": hand.winner_jack.id if hand.winner_jack else None,
                "winner_game": hand.winner_game.id if hand.winner_game else None,
            }
            if hand.finished
            else None
        )

    class Meta:
        model = Hand
        fields = ("id", "num", "dealer", "bidder", "high_bid", "trump", "bids", "cards", "results", "finished")


class StatusBiddingSerializer(serializers.ModelSerializer):
    current_hand = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()
    teams = TeamSummarySerializer(read_only=True, many=True)

    class Meta:
        model = Game
        fields = ("state", "current_hand", "players", "teams")

    def get_current_hand(self, game):
        hand = self.context.get("hand")
        return HandSummaryWithCardsSerializer(hand, read_only=True, context=self.context).data if hand else {}

    def get_players(self, game):
        hand = self.context.get("hand")
        player_context = {
            **self.context,
            "game_points_by_player": hand.game_points_by_player,
        }
        # Ordering by seat invalidates our prefetch_related, so we'll order in the app
        players_unsorted = game.player_set.all()
        players = sort_by_seat_if_present(players_unsorted)
        return PlayerSummarySerializer(players, many=True, read_only=True, context=player_context).data


class TrickSummarySerializer(serializers.ModelSerializer):
    plays = PlaySerializer(read_only=True, many=True)

    class Meta:
        model = Trick
        fields = ("id", "num", "active_player", "taker", "plays")


class StatusPlayingTrickSerializer(serializers.ModelSerializer):
    current_hand = serializers.SerializerMethodField()
    current_trick = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()
    teams = TeamSummarySerializer(read_only=True, many=True)

    class Meta:
        model = Game
        fields = ("state", "current_hand", "current_trick", "players", "teams")

    def get_current_hand(self, game):
        hand = self.context.get("hand")
        return HandSummaryWithCardsSerializer(hand, read_only=True, context=self.context).data if hand else {}

    def get_current_trick(self, game):
        trick = self.context.get("trick")
        return TrickSummarySerializer(trick, read_only=True, context=self.context).data if trick else {}

    def get_state(self, game):
        trick_num = self.context.get("trick_num")
        # Force PLAYING_TRICK if user asks for trick specifically
        return Game.PLAYING_TRICK if trick_num else game.state

    def get_players(self, game):
        hand = self.context.get("hand")
        player_context = {
            **self.context,
            "game_points_by_player": hand.game_points_by_player,
        }
        # Ordering by seat invalidates our prefetch_related, so we'll order in the app
        players_unsorted = game.player_set.all()
        players = sort_by_seat_if_present(players_unsorted)
        return PlayerSummarySerializer(players, many=True, read_only=True, context=player_context).data


class GameSerializer(serializers.ModelSerializer):
    passcode = serializers.CharField(write_only=True, required=False, allow_blank=True)
    players = serializers.SerializerMethodField()
    teams = TeamSummarySerializer(read_only=True, many=True)

    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ("owner", "passcode_required", "name")

    def get_players(self, game):
        # Ordering by seat invalidates our prefetch_related, so we'll order in the app
        players_unsorted = game.player_set.all()
        players = sort_by_seat_if_present(players_unsorted)
        return PlayerSummarySerializer(players, many=True, read_only=True, context=self.context).data


class GameDetailSerializer(GameSerializer):
    current_hand = serializers.SerializerMethodField()
    current_trick = serializers.SerializerMethodField()

    def get_current_hand(self, game):
        hand = self.context.get("hand")
        if not hand:
            hand_num = self.context.get("hand_num")
            hand = Hand.objects.get(game=game, num=hand_num) if hand_num else game.current_hand
            self.context["hand"] = hand
        return HandSummaryWithCardsSerializer(hand, read_only=True, context=self.context).data if hand else {}

    def get_current_trick(self, game):
        trick = self.context.get("trick")
        if not trick:
            hand = self.context.get("hand")
            if not hand:
                hand_num = self.context.get("hand_num")
                hand = Hand.objects.get(game=game, num=hand_num) if hand_num else game.current_hand
                self.context["hand"] = hand
            trick_num = self.context.get("trick_num")
            trick = Trick.objects.get(hand=hand, num=trick_num) if trick_num else game.current_trick
            self.context["trick"] = trick
        return TrickSummarySerializer(trick, read_only=True, context=self.context).data if trick else {}


class GameJoinSerializer(serializers.Serializer):
    passcode = serializers.CharField(max_length=512, required=False)

 
class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ("id", "bid", "trump", "player")
        read_only_fields = ("player",)
        write_only_fields = ("trump",)
        extra_kwargs = {"trump": {"write_only": True}}

    def validate_bid(self, value):
        try:
            hand = self.context["extra_kwargs"]["hand"]
        except KeyError:
            raise ValidationError(
                "context not set up correctly, extra_kwargs needs to be present with the hand passed in"
            )

        if value < 0 or value == 1 or value > 5:
            raise ValidationError(f"A bid of {value} is not a legal bid. Bids must be 0 (pass) or between 2 and 5")

        if value != 0 and hand.high_bid and hand.high_bid.bid >= value:
            raise ValidationError(f"Unable to bid {value}, there is already a bid of {hand.high_bid.bid}")

        return value

    def validate_trump(self, value):
        if value.lower() not in SUITS:
            raise ValidationError(f"{value} is not a valid suit")

        return value.lower()
