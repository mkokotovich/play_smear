from random import shuffle
import logging
from functools import reduce

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
    next_dealer = models.ForeignKey('Player', related_name='games_next_dealer', on_delete=models.CASCADE, null=True, blank=True)

    # Available states
    STARTING = "starting"
    NEW_HAND = "new_hand"
    BIDDING = "bidding"
    DECLARING_TRUMP = "declaring_trump"
    PLAYING_TRICK = "playing_trick"

    def set_state(self, new_state):
        # For now just set state. At some point we might invalidate cache
        self.state = new_state
        self.save()

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.name} ({self.id})"

    @property
    def current_hand(self):
        return self.hands.last()

    @property
    def current_trick(self):
        return self.hands.last().tricks.last()

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
        self.next_dealer = self.set_plays_after()
        LOG.info(f"Starting game {self} with players {', '.join([str(p) for p in self.player_set.all()])}")

        self.set_state(Game.NEW_HAND)
        self.advance_game()

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
        if self.state == Game.NEW_HAND:
            hand = Hand.objects.create(game=self)
            hand.start(dealer=self.next_dealer)
            self.next_dealer = self.next_player(self.next_dealer)
            self.set_state(Game.BIDDING)
            self.save()
            self.current_hand.advance_bidding()
        elif self.state == Game.BIDDING:
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
        trump_value = self.cards_in_hand[0][1]

        LOG.info(f"{self} has {self.cards_in_hand}, bidding {bid_value} in {trump_value}")
        return Bid.create_bid_for_player(bid_value, trump_value, self, self.game.current_hand)

    def play_card(self):
        # TODO: playing logic
        card = self.cards_in_hand.pop(0)
        return Card(representation=card)


class Hand(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    game = models.ForeignKey(Game, related_name='hands', on_delete=models.CASCADE, null=True)
    dealer = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    bidder = models.ForeignKey(Player, related_name='hands_was_bidder', on_delete=models.CASCADE, null=True, blank=True)
    high_bid = models.OneToOneField('smear.Bid', related_name='hand_with_high_bid', on_delete=models.SET_NULL, null=True, blank=True)
    trump = models.CharField(max_length=16, blank=True, default="")

    # We calculate the high and low at the beginning
    # This is so we don't need to keep all the cards players have 'won',
    # we can just keep a running tally of who won which points
    high_card = models.CharField(max_length=2, blank=True, default="")
    low_card = models.CharField(max_length=2, blank=True, default="")
    # These values are updated as players win the cards, but game is
    # awarded at the end of the game
    winner_high = models.ForeignKey(Player, related_name="games_winner_high", on_delete=models.CASCADE, null=True, blank=True)
    winner_low = models.ForeignKey(Player, related_name="games_winner_low", on_delete=models.CASCADE, null=True, blank=True)
    winner_jack = models.ForeignKey(Player, related_name="games_winner_jack", on_delete=models.CASCADE, null=True, blank=True)
    winner_jick = models.ForeignKey(Player, related_name="games_winner_jick", on_delete=models.CASCADE, null=True, blank=True)
    winner_game = models.ForeignKey(Player, related_name="games_winner_game", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Hand {self.id} (dealer: {self.dealer}) (bidder: {self.bidder}) (high_bid: {self.high_bid}) (trump: {self.trump})"

    def start(self, dealer):
        LOG.info("Starting hand with dealer: {dealer}")
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
        self.high_bid = self.high_bid if (self.high_bid and self.high_bid.bid >= new_bid.bid) else new_bid
        finished_bidding = self.bidder == self.dealer
        self.bidder = self.game.next_player(self.bidder)
        LOG.info(f"Submitted bid {new_bid}, high bid is now {self.high_bid}, bidder is now {self.bidder}")
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
        self.bidder = self.high_bid.player
        self.game.set_state(Game.DECLARING_TRUMP)

        LOG.info(f"{self.bidder} has the high bid of {self.high_bid}")

        if self.high_bid.trump:
            self.finalize_trump_declaration(self.high_bid.trump)

    @staticmethod
    def _reduce_find_low_trump(accum, player):
        trump, current_low = accum
        trump_cards = [card for card in player.get_cards() if card.suit == trump]
        lowest_trump = min(trump_cards, key=lambda x: x.rank()) if trump_cards else None
        current_low = current_low if (lowest_trump is None or (current_low and current_low.rank() < lowest_trump.rank())) else lowest_trump
        return trump, current_low

    @staticmethod
    def _reduce_find_high_trump(accum, player):
        trump, current_high = accum
        trump_cards = [card for card in player.get_cards() if card.suit == trump]
        highest_trump = max(trump_cards, key=lambda x: x.rank()) if trump_cards else None
        current_high = current_high if (highest_trump is None or (current_high and current_high.rank() > highest_trump.rank())) else highest_trump
        return trump, current_high

    def finalize_trump_declaration(self, trump):
        """Now that we know trump, we will figure out what the high
        and low are, so we can watch and award those when won
        """
        self.trump = trump
        self.low_card = reduce(
            Hand._reduce_find_low_trump,
            list(self.game.player_set.all()),
            (self.trump, None)
        )
        self.high_card = reduce(
            Hand._reduce_find_high_trump,
            list(self.game.player_set.all()),
            (self.trump, None)
        )
        LOG.info(f"Trump is {self.trump}, high will be {self.high_card} and low will be {self.low_card}")
        self.advance_hand()

    def advance_hand(self):
        if self.game.state == Game.BIDDING:
            self.advance_bidding()
        elif self.game.state == Game.DECLARING_TRUMP:
            trick = Trick.objects.create(hand=self)
            trick.start(self.bidder)
            self.game.set_state(Game.PLAYING_TRICK)
            trick.advance_trick()
        elif self.game.state == Game.PLAYING_TRICK:
            # game.advance_hand() is only called when trick is finished
            # Check to see if hand is finished, otherwise start next trick
            if self.tricks.count() == 6:
                # TODO - award game point
                self.game.set_state(Game.DECLARING_TRUMP)
                self.game.advance_game()
            else:
                trick = Trick.objects.create(hand=self)
                trick.start(self.bidder)
                trick.advance_trick()

    def player_can_change_bid(self, player):
        next_bidder = self.bidder
        if player == next_bidder:
            return True
        while next_bidder != self.dealer:
            next_bidder = next_bidder.plays_before
            if player == next_bidder:
                return True
        return False


class Bid(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    hand = models.ForeignKey(Hand, related_name='bids', on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(Player, related_name='bids', on_delete=models.CASCADE, null=True)
    bid = models.IntegerField()
    trump = models.CharField(max_length=16, blank=True, default="")

    def __str__(self):
        return f"{self.bid} (by {self.player})"

    @staticmethod
    def create_bid_for_player(bid, trump, player, hand):
        return Bid.objects.create(bid=bid, trump=trump, player=player, hand=hand)


class Trick(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    hand = models.ForeignKey(Hand, related_name='tricks', on_delete=models.CASCADE, null=True)
    cards_played = ArrayField(
        models.CharField(max_length=2),
        default=list
    )
    active_player = models.ForeignKey(Player, related_name='tricks_playing', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{', '.join(self.cards_played)} ({self.id})"

    def submit_card_to_play(self, card, player):
        """Handles validation of the card's legality

        Returns:
            trick_finished (bool): whether or not the trick is finished
        """
        # TODO Validate card is legal
        if player != self.active_player:
            raise ValidationError(f"It is not {player}'s turn to play")

        LOG.info(f"{player} played {card}")
        self.cards_played.append(card.to_representation())
        self.active_player = self.hand.game.next_player(self.active_player)
        self.save()
        return len(self.cards_played) == self.hand.game.num_players

    def play_card(self, card):
        trick_finished = self.submit_card_to_play(card)
        if trick_finished:
            self._finalize_trick()
        else:
            self.advance_trick()

    def get_cards(self):
        return [Card(representation=rep) for rep in self.cards_played]

    def start(self, player_who_leads):
        LOG.info(f"Starting trick with {player_who_leads} leading")
        self.active_player = player_who_leads

    def advance_trick(self):
        """Advances any computers playing
        """
        trick_finished = False
        while not trick_finished:
            if self.active_player.is_computer:
                # Have computer choose a card to play, then play it
                card_to_play = self.active_player.play_card()
                trick_finished = self.submit_card_to_play(card_to_play, self.active_player)
            else:
                # Waiting for a human to play, just return
                return

        self._finalize_trick()

    def _finalize_trick():
        LOG.info(f"Trick is finished. Cards played: {self.cards_played}")
        # TODO - find out who won the trick, award them the cards and any points
        self.hand.advance_hand()
