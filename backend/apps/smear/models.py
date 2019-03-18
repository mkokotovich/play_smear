from random import shuffle
import logging

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from rest_framework.exceptions import ValidationError

from apps.smear.cards import Card, Deck


LOG = logging.getLogger(__name__)


class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey('auth.User', related_name='games', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=256, blank=True, default="")
    num_players = models.IntegerField()
    num_teams = models.IntegerField()
    score_to_play_to = models.IntegerField()
    passcode_required = models.BooleanField(blank=True, default=False)
    passcode = models.CharField(max_length=256, blank=True, default="")
    single_player = models.BooleanField(blank=False, default=True)
    players = models.ManyToManyField('auth.User', through='Player')
    state = models.CharField(max_length=1024, blank=True, default="")

    # Available states
    STARTING = "starting"
    BIDDING = "bidding"
    DECLARING_TRUMP = "declaring_trump"

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.name} ({self.id})"

    @property
    def current_hand(self):
        return self.hands.last()

    def next_player(self, player):
        # TODO determine if this is really more performant
        # next_seat = (player.seat + 1) % self.num_players
        # return self.player_set.get(seat=next_seat)
        return player.plays_before

    def create_initial_teams(self):
        for i in range(0, self.num_teams):
            Team.objects.create(game=self, name=f"Team {i+1}")

    def add_computer_player(self):
        if self.players.count() >= self.num_players:
            raise ValidationError(f"Unable to add computer, game already contains {self.num_players} players")

        computers = list(User.objects.filter(username__startswith="mkokotovich+computer").all())
        shuffle(computers)
        for computer in computers:
            if not self.players.filter(id=computer.id).exists():
                computer_player = Player.objects.create(
                    game=self,
                    user=computer,
                    is_computer=True
                )
                LOG.info(f"Added computer {computer} to {self}")
                return computer_player

    def autofill_teams(self):
        if self.num_teams == 0:
            return
        teams = self.teams.all()
        players = list(self.player_set.all())
        shuffle(players)

        for player_num, player in enumerate(players):
            team_num = player_num % self.num_teams
            player.team = teams[team_num]
            player.save()
            LOG.info(f"Autofilling teams for game {self}. Added {player} to team {teams[team_num]}")

    def reset_teams(self):
        for team in self.teams.all():
            team.members.clear()

    def start(self):
        if self.players.count() != self.num_players:
            raise ValidationError(f"Unable to start game, game requires {self.num_players} players, but {self.players.count()} have joined")

        self.set_seats()
        first_dealer = self.set_plays_after()

        hand = Hand.objects.create(game=self)
        hand.start(dealer=first_dealer)
        self.state = Game.BIDDING
        self.advance_game()
        self.save()
        LOG.info(f"Started hand {hand} on game {self}")

    def set_seats(self):
        # Assign players to their seats
        total_players = 0
        for team_num, team in enumerate(self.teams.all()):
            for player_num, player in enumerate(team.members.all()):
                player.seat = team_num + (self.num_teams * player_num)
                LOG.info(f"Added {player.name} from game {self.name} and team {team.name} to seat {player.seat}")
                player.save()
                total_players += 1

        if not self.teams.exists():
            for player_num, player in enumerate(self.player_set.all()):
                player.seat = player_num
                LOG.info(f"Added {player.name} from game {self.name} to seat {player.seat}")
                player.save()
                total_players += 1

        if total_players != self.num_players:
            raise ValidationError(f"Unable to start game, only {total_players} were assigned to teams, but {self.num_players} are playing")

    def set_plays_after(self):
        players = list(self.player_set.all().order_by('seat'))
        prev_player = players[-1]
        for player in players:
            player.plays_after = prev_player
            player.save()
            prev_player = player
        return players[0]

    def advance_game(self):
        if self.state == Game.BIDDING:
            self.current_hand.advance_bidding()


class Team(models.Model):
    game = models.ForeignKey(Game, related_name='teams', on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.name} ({self.id})"


class Player(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    is_computer = models.BooleanField(blank=True, default=False)
    name = models.CharField(max_length=1024)
    team = models.ForeignKey(Team, related_name='members', on_delete=models.CASCADE, null=True, blank=True)
    seat = models.IntegerField(blank=True, null=True)
    plays_after = models.OneToOneField('smear.Player', related_name='plays_before', on_delete=models.SET_NULL, null=True, blank=True)

    cards_in_hand = ArrayField(
        models.CharField(max_length=2),
        default=list
    )

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name', self._get_name_from_user(kwargs.get('user', None)))
        super().__init__(name=name, *args, **kwargs)

    def _get_name_from_user(self, user):
        if not user:
            return 'Unknown'
        name = user.first_name + f"{' ' + user.last_name[:1] if user.last_name else ''}"
        if not name:
            name = user.username.split('@')[0]
        return name

    def accept_dealt_cards(self, cards):
        representations = [card.to_representation() for card in cards]
        self.cards_in_hand.extend(representations)
        self.save()

    def get_cards(self):
        return [Card(representation=rep) for rep in self.cards_in_hand]

    def create_bid(self):
        # TODO: bidding logic
        bid_value = 2
        return Bid.create_bid_for_player(bid_value, self, self.game.current_hand)

    def declare_trump(self):
        # TODO: where do we store this when we bid?
        return "S"


class Hand(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    game = models.ForeignKey(Game, related_name='hands', on_delete=models.CASCADE, null=True)
    dealer = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    bidder = models.ForeignKey(Player, related_name='hands_was_bidder', on_delete=models.CASCADE, null=True, blank=True)
    high_bid = models.OneToOneField('smear.Bid', related_name='hand_with_high_bid', on_delete=models.SET_NULL, null=True, blank=True)
    trump = models.CharField(max_length=16, blank=True, default="")

    def start(self, dealer):
        # Set the dealer
        self.dealer = dealer
        self.bidder = self.game.next_player(dealer)

        # Deal out six cards
        deck = Deck()
        for player in self.game.player_set.all():
            player.accept_dealt_cards(deck.deal(3))
        for player in self.game.player_set.all():
            player.accept_dealt_cards(deck.deal(3))

        self.save()

    def submit_bid(self, new_bid):
        if new_bid.player.id != self.bidder.id:
            raise ValidationError(f"It is not {new_bid.player}'s turn to bid")
        self.high_bid = self.high_bid if (self.high_bid and self.high_bid.bid > new_bid.bid) else new_bid
        finished_bidding = self.bidder == self.dealer
        self.bidder = self.game.next_player(self.bidder)
        self.save()
        return finished_bidding

    def advance_bidding(self):
        finished_bidding = False
        while not finished_bidding:
            bid_filter = self.bidder.bids.filter(hand=self)
            if bid_filter.exists():
                # A human's bid exists, submit it
                finished_bidding = self.submit_bid(bid_filter[0])
            elif self.bidder.is_computer:
                # Generate computer bid and submit it
                bid = self.bidder.create_bid()
                finished_bidding = self.submit_bid(bid)
            else:
                # Waiting for a human to bid, just return
                return

        self._finalize_bidding()

    def _finalize_bidding(self):
        self.high_bid = self.bids.order_by('-bid').first()
        self.bidder = self.high_bid.player
        self.game.state = Game.DECLARING_TRUMP

        LOG.info(f"{self.bidder} has the high bid of {self.high_bid}")

        if self.bidder.is_computer:
            trump = self.bidder.declare_trump()
            self.finalize_trump_declaration(trump)

    def finalize_trump_declaration(self, trump):
        self.trump = trump
        self.advance_trick()

    def advance_trick(self):
        pass


class Bid(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    hand = models.ForeignKey(Hand, related_name='bids', on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(Player, related_name='bids', on_delete=models.CASCADE, null=True)
    bid = models.IntegerField()
    trump = models.CharField(max_length=16, blank=True, default="")

    def __str__(self):
        return f"{self.bid} ({self.id})"

    @staticmethod
    def create_bid_for_player(bid, player, hand):
        return Bid.objects.create(bid=bid, player=player, hand=hand)
