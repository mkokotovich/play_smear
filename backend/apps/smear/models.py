from random import shuffle
import logging
from functools import reduce

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from rest_framework.exceptions import ValidationError

from apps.smear.cards import Card, Deck, SUIT_CHOICES


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
        hand = self.hands.last()
        return hand.tricks.last() if hand else None

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

    def start_game(self):
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
            hand = Hand.objects.create(game=self, num=self.hands.count() + 1)
            hand.start_hand(dealer=self.next_dealer)
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

    def reset_for_new_hand(self):
        self.cards_in_hand = []
        self.save()

    def accept_dealt_cards(self, cards):
        representations = [card.to_representation() for card in cards]
        self.cards_in_hand.extend(representations)
        self.save()

    def get_cards(self):
        return [Card(representation=rep) for rep in self.cards_in_hand]

    def create_bid(self):
        # TODO: bidding logic
        bid_value = 2
        trump_value = Card(representation=self.cards_in_hand[0]).suit

        LOG.info(f"{self} has {self.cards_in_hand}, bidding {bid_value} in {trump_value}")
        return Bid.create_bid_for_player(bid_value, trump_value, self, self.game.current_hand)

    def play_card(self):
        # TODO: playing logic
        card = self.cards_in_hand[0]
        return Card(representation=card)

    def card_played(self, card):
        self.cards_in_hand.remove(card.to_representation())
        self.save()


class Hand(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # num is the number hand in the game, starting at 1
    num = models.IntegerField()

    game = models.ForeignKey(Game, related_name='hands', on_delete=models.CASCADE, null=True)
    dealer = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    bidder = models.ForeignKey(Player, related_name='hands_was_bidder', on_delete=models.CASCADE, null=True, blank=True)
    high_bid = models.OneToOneField('smear.Bid', related_name='hand_with_high_bid', on_delete=models.SET_NULL, null=True, blank=True)
    trump = models.CharField(max_length=16, blank=True, default="", choices=SUIT_CHOICES)

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

    class Meta:
        unique_together = (('game', 'num'),)

    def __str__(self):
        return f"Hand {self.id} (dealer: {self.dealer}) (bidder: {self.bidder}) (high_bid: {self.high_bid}) (trump: {self.trump})"

    def start_hand(self, dealer):
        LOG.info(f"Starting hand with dealer: {dealer}")
        # Set the dealer
        self.dealer = dealer
        self.bidder = self.game.next_player(dealer)

        # Deal out six cards
        deck = Deck()
        players = self.game.player_set.all()
        for player in players:
            player.reset_for_new_hand()
            player.accept_dealt_cards(deck.deal(3))
        for player in players:
            player.accept_dealt_cards(deck.deal(3))

        self.save()

    def add_bid_to_hand(self, new_bid):
        self.high_bid = self.high_bid if (self.high_bid and self.high_bid.bid >= new_bid.bid) else new_bid
        finished_bidding = self.bidder == self.dealer
        self.bidder = self.game.next_player(self.bidder)
        LOG.info(f"Submitted bid {new_bid}, high bid is now {self.high_bid}, bidder is now {self.bidder}, finished_bidding is {finished_bidding}")
        self.save()
        return finished_bidding

    def submit_bid(self, new_bid):
        if new_bid.player.id != self.bidder.id:
            raise ValidationError(f"It is not {new_bid.player}'s turn to bid")
        finished_bidding = self.add_bid_to_hand(new_bid)
        self.advance_bidding(finished_bidding)

    def advance_bidding(self, finished_bidding_arg=False):
        finished_bidding = finished_bidding_arg
        while not finished_bidding:
            bid_filter = self.bidder.bids.filter(hand=self)
            if bid_filter.exists():
                # A human's bid exists, submit it
                finished_bidding = self.add_bid_to_hand(bid_filter[0])
            elif self.bidder.is_computer:
                # Generate computer bid and submit it
                bid = self.bidder.create_bid()
                finished_bidding = self.add_bid_to_hand(bid)
            else:
                # Waiting for a human to bid, just return
                return

        self._finalize_bidding()

    def _finalize_bidding(self):
        self.bidder = self.high_bid.player
        self.save()
        self.game.set_state(Game.DECLARING_TRUMP)

        LOG.info(f"{self.bidder} has the high bid of {self.high_bid}")

        if self.high_bid.trump:
            self.finalize_trump_declaration(self.high_bid.trump)

    @staticmethod
    def _reduce_find_low_trump(accum, player):
        trump, current_low = accum
        trump_cards = [card for card in player.get_cards() if card.suit == trump]
        lowest_trump = min(trump_cards, key=lambda x: x.rank()) if trump_cards else None
        new_low = current_low if (lowest_trump is None or (current_low and current_low.rank() < lowest_trump.rank())) else lowest_trump
        return trump, new_low

    @staticmethod
    def _reduce_find_high_trump(accum, player):
        trump, current_high = accum
        trump_cards = [card for card in player.get_cards() if card.suit == trump]
        highest_trump = max(trump_cards, key=lambda x: x.rank()) if trump_cards else None
        new_high = current_high if (highest_trump is None or (current_high and current_high.rank() > highest_trump.rank())) else highest_trump
        return trump, new_high

    def finalize_trump_declaration(self, trump):
        """Now that we know trump, we will figure out what the high
        and low are, so we can watch and award those when won
        """
        self.trump = trump
        _, self.low_card = reduce(
            Hand._reduce_find_low_trump,
            list(self.game.player_set.all()),
            (self.trump, None)
        )
        _, self.high_card = reduce(
            Hand._reduce_find_high_trump,
            list(self.game.player_set.all()),
            (self.trump, None)
        )
        self.save()
        LOG.info(f"Trump is {self.trump}, high will be {self.high_card} and low will be {self.low_card}")
        self.advance_hand()

    def advance_hand(self):
        if self.game.state == Game.BIDDING:
            self.advance_bidding()
        elif self.game.state == Game.DECLARING_TRUMP:
            trick = Trick.objects.create(hand=self, num=self.tricks.count() + 1)
            trick.start_trick(self.bidder)
            self.game.set_state(Game.PLAYING_TRICK)
            trick.advance_trick()
        elif self.game.state == Game.PLAYING_TRICK:
            # game.advance_hand() is only called when trick is finished
            # Check to see if hand is finished, otherwise start next trick
            if self.tricks.count() == 6:
                self._finalize_hand()
                self.game.set_state(Game.NEW_HAND)
                self.game.advance_game()
            else:
                trick = Trick.objects.create(hand=self, num=self.tricks.count() + 1)
                trick.start_trick(self.bidder)
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

    def _finalize_hand(self):
        LOG.info("Hand is finished")
        # TODO - award game point
        pass


class Bid(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    hand = models.ForeignKey(Hand, related_name='bids', on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(Player, related_name='bids', on_delete=models.CASCADE, null=True)
    bid = models.IntegerField()
    trump = models.CharField(max_length=16, blank=True, default="", choices=SUIT_CHOICES)

    def __str__(self):
        return f"{self.bid} (by {self.player})"

    @staticmethod
    def create_bid_for_player(bid, trump, player, hand):
        return Bid.objects.create(bid=bid, trump=trump, player=player, hand=hand)


class Play(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    trick = models.ForeignKey('Trick', related_name='plays', on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(Player, related_name='plays', on_delete=models.CASCADE, null=True)
    card = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.card} (by {self.player})"


class Trick(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # num is the number trick of the hand (e.g. 1, 2, 3, 4, 5, and then 6)
    num = models.IntegerField()

    hand = models.ForeignKey(Hand, related_name='tricks', on_delete=models.CASCADE, null=True)
    active_player = models.ForeignKey(Player, related_name='tricks_playing', on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (('hand', 'num'),)

    def __str__(self):
        return f"{', '.join(self.plays.all())} ({self.id})"

    def submit_card_to_play(self, card, player):
        """Handles validation of the card's legality

        Returns:
            trick_finished (bool): whether or not the trick is finished
        """
        # TODO Validate card is legal
        if player != self.active_player:
            raise ValidationError(f"It is not {player}'s turn to play")

        LOG.info(f"{player} played {card}")
        self.active_player = self.hand.game.next_player(self.active_player)
        self.save()

        # Officially "play" the card, if the play hasn't already been created in the view
        play, created = Play.objects.get_or_create(card=card.to_representation(), player=player, trick=self)

        # Let the player know to remove card from hand
        player.card_played(card)

        return self.plays.count() == self.hand.game.num_players

    def submit_play(self, play):
        card = Card(representation=play.card)
        trick_finished = self.submit_card_to_play(card, play.player)
        self.advance_trick(trick_finished)

    def get_cards(self, as_rep=False):
        cards = [play.card for play in self.plays.all()]
        return [Card(representation=rep) for rep in cards] if not as_rep else cards

    def get_lead_play(self):
        return self.plays.first() if self.plays.exists() else None

    def start_trick(self, player_who_leads):
        LOG.info(f"Starting trick with {player_who_leads} leading")
        self.active_player = player_who_leads
        self.save()

    def advance_trick(self, trick_finished_arg=False):
        """Advances any computers playing
        """
        trick_finished = trick_finished_arg
        while not trick_finished:
            if self.active_player.is_computer:
                # Have computer choose a card to play, then play it
                card_to_play = self.active_player.play_card()
                trick_finished = self.submit_card_to_play(card_to_play, self.active_player)
            else:
                # Waiting for a human to play, just return
                return

        self._finalize_trick()

    def award_cards_to_taker(self):
        # TODO - find out who won the trick, award them the game points and any points
        return self.get_lead_play().player

    def _finalize_trick(self):
        taker = self.award_cards_to_taker()
        LOG.info(f"Trick is finished. {taker} took the following cards: {self.get_cards()}")
        self.hand.advance_hand()

    def player_can_change_play(self, player):
        # TODO - do we want to allow async play submission?
        return False
