from random import shuffle
import logging

from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils.functional import cached_property
from rest_framework.exceptions import ValidationError

from apps.smear.cards import Card, Deck, SUIT_CHOICES
from apps.smear.computer_logic import computer_bid, computer_play_card


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
    GAME_OVER = "game_over"

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
    score = models.IntegerField(blank=True, default=0)
    winner = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return f"{self.name} ({self.id})"


class Player(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, default=0)
    winner = models.BooleanField(blank=True, default=False)

    is_computer = models.BooleanField(blank=True, default=False)
    name = models.CharField(max_length=1024)
    team = models.ForeignKey(Team, related_name='members', on_delete=models.CASCADE, null=True, blank=True)
    seat = models.IntegerField(blank=True, null=True)
    plays_after = models.OneToOneField('smear.Player', related_name='plays_before', on_delete=models.SET_NULL, null=True, blank=True)

    cards_in_hand = ArrayField(
        models.CharField(max_length=2),
        default=list
    )
    current_hand_game_points_won = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.name:
            self.name = self._get_name_from_user(kwargs.get("user", None))

    def _get_name_from_user(self, user):
        if not user:
            return 'Unknown'
        name = user.first_name + f"{' ' + user.last_name[:1] if user.last_name else ''}"
        if not name:
            name = user.username.split('@')[0]
        return name

    def reset_for_new_hand(self):
        self.cards_in_hand = []
        self.current_hand_game_points_won = 0
        self.save()

    def accept_dealt_cards(self, cards):
        representations = [card.to_representation() for card in cards]
        self.cards_in_hand.extend(representations)
        self.save()

    def get_cards(self):
        return [Card(representation=rep) for rep in self.cards_in_hand]

    def create_bid(self, hand):
        bid_value, trump_value = computer_bid(self, hand)

        LOG.info(f"{self} has {self.cards_in_hand}, bidding {bid_value}{' in ' + trump_value if bid_value else ''}")
        return Bid.create_bid_for_player(bid_value, trump_value, self, self.game.current_hand)

    def play_card(self, trick):
        card = computer_play_card(self, trick)

        LOG.info(f"{self} has {self.cards_in_hand}, playing {card}")
        return card

    def card_played(self, card):
        self.cards_in_hand.remove(card.to_representation())
        self.save()

    def increment_score(self):
        if self.team:
            self.team.score = F('score') + 1
            self.team.save()
        else:
            self.score = F('score') + 1
            self.save()

    def decrement_score(self, amount):
        if self.team:
            self.team.score = F('score') - amount
            self.team.save()
        else:
            self.score = F('score') - amount
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

    # These values are updated as players win the cards, but game is
    # awarded at the end of the game
    winner_high = models.ForeignKey(Player, related_name="games_winner_high", on_delete=models.CASCADE, null=True, blank=True)
    winner_low = models.ForeignKey(Player, related_name="games_winner_low", on_delete=models.CASCADE, null=True, blank=True)
    winner_jack = models.ForeignKey(Player, related_name="games_winner_jack", on_delete=models.CASCADE, null=True, blank=True)
    winner_jick = models.ForeignKey(Player, related_name="games_winner_jick", on_delete=models.CASCADE, null=True, blank=True)
    winner_game = models.ForeignKey(Player, related_name="games_winner_game", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['num']
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
        if self.high_bid and new_bid.bid <= self.high_bid.bid and new_bid.bid != 0:
            # User bid the same as the current bid, invalid
            raise ValueError(f"Unable to bid {new_bid.bid} when the current high bid is {self.high_bid.bid}")
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
                bid = self.bidder.create_bid(self)
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

    def award_low_trump(self):
        current_low = None
        current_low_winner = None
        for player in self.game.player_set.all():
            trump_cards = [card for card in player.get_cards() if card.suit == self.trump]
            lowest_trump = min(trump_cards, key=lambda x: x.rank()) if trump_cards else None
            new_low = current_low if (lowest_trump is None or (current_low and current_low.rank() < lowest_trump.rank())) else lowest_trump
            if new_low != current_low and new_low is not None:
                current_low = new_low
                current_low_winner = player
        self.winner_low = current_low_winner
        LOG.info(f"Awarding low to {self.winner_low} - low is {current_low}")

    def award_high_trump(self):
        current_high = None
        current_high_winner = None
        for player in self.game.player_set.all():
            trump_cards = [card for card in player.get_cards() if card.suit == self.trump]
            highest_trump = max(trump_cards, key=lambda x: x.rank()) if trump_cards else None
            new_high = current_high if (highest_trump is None or (current_high and current_high.rank() > highest_trump.rank())) else highest_trump
            if new_high != current_high and new_high is not None:
                current_high = new_high
                current_high_winner = player
        self.winner_high = current_high_winner
        LOG.info(f"Awarding high to {self.winner_high} - high is {current_high}")

    def finalize_trump_declaration(self, trump):
        """Now that we know trump, we will figure out what the high
        and low are and "award" them in advance
        """
        LOG.info(f"Trump is {trump}")
        self.trump = trump
        self.award_low_trump()
        self.award_high_trump()
        self.save()
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
                game_is_over = self._finalize_hand()
                new_state = Game.GAME_OVER if game_is_over else Game.NEW_HAND
                self.game.set_state(new_state)
                self.game.advance_game()
            else:
                last_taker = self.tricks.last().taker
                trick = Trick.objects.create(hand=self, num=self.tricks.count() + 1)
                trick.start_trick(last_taker)
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

    def award_game(self):
        # TODO - award game point
        # Take into account teams
        self.winner_game = self.bidder
        LOG.info(f"Awarding game to {self.winner_game}")

    def _declare_winner_if_game_is_over(self):
        # This function deals with players or teams. We will use the generic
        # noun contestants to describe either
        teams = self.game.teams.exists()
        winners = None
        contestants = self.game.teams.all() if teams else self.game.player_set.all()
        contestants_at_or_over = list(contestants.filter(score__gte=self.game.score_to_play_to))
        game_is_over = bool(contestants_at_or_over)

        if game_is_over:
            bidding_contestant = self.bidder.team if teams else self.bidder
            if bidding_contestant in contestants_at_or_over:
                # Bidder always goes out
                bidding_contestant.refresh_from_db()
                high_score = bidding_contestant.score
                winners = [bidding_contestant]
            else:
                high_scorer = max(contestants_at_or_over, key=lambda c: c.score)
                high_scorer.refresh_from_db()
                high_score = high_scorer.score
                # Accounting for the unlikely scenario of a tie
                winners = [contestant for contestant in contestants_at_or_over if contestant.score == high_score]
                LOG.info(f"high_score: {high_score} c_a_o_o: {contestants_at_or_over} winners: {winners}")

            for winner in winners:
                winner.winner = True
                winner.save()

            LOG.info(f"Game Over! Winners are {winners} with a score of {high_score}")

        return game_is_over

    def _calculate_if_bid_was_won(self):
        teammate_ids = (
            [self.bidder.id]
            if self.bidder.team is None else
            self.bidder.team.members.values_list('id', flat=True)
        )

        bidders_points = 0
        if self.winner_high and self.winner_high.id in teammate_ids:
            bidders_points += 1
        if self.winner_low and self.winner_low.id in teammate_ids:
            bidders_points += 1
        if self.winner_jick and self.winner_jick.id in teammate_ids:
            bidders_points += 1
        if self.winner_jack and self.winner_jack.id in teammate_ids:
            bidders_points += 1
        if self.winner_game and self.winner_game.id in teammate_ids:
            bidders_points += 1

        bid_won = bidders_points >= self.high_bid.bid
        LOG.info(f"{self.bidder} bid {self.high_bid.bid} and got {bidders_points}: {'was not' if bid_won else 'was'} set")
        return bid_won, teammate_ids

    def _refresh_all_scores(self):
        contestants = self.game.teams.all() if self.game.teams.exists() else self.game.player_set.all()
        for contestant in contestants:
            contestant.refresh_from_db(fields=['score'])

    def _finalize_hand(self):
        self.award_game()
        self.save()
        LOG.info(
            f"Hand is finished. High: {self.winner_high} "
            f"Low: {self.winner_low} Jack: {self.winner_jack} "
            f"Jick: {self.winner_jick} Game: {self.winner_game}"
        )
        bid_won, teammate_ids = self._calculate_if_bid_was_won()
        if not bid_won:
            self.bidder.decrement_score(self.high_bid.bid)

        # Award the points, but not to the bidder if the bidder was set
        if self.winner_high and (bid_won or self.winner_high.id not in teammate_ids):
            self.winner_high.increment_score()
        if self.winner_low and (bid_won or self.winner_low.id not in teammate_ids):
            self.winner_low.increment_score()
        if self.winner_jick and (bid_won or self.winner_jick.id not in teammate_ids):
            self.winner_jick.increment_score()
        if self.winner_jack and (bid_won or self.winner_jack.id not in teammate_ids):
            self.winner_jack.increment_score()
        if self.winner_game and (bid_won or self.winner_game.id not in teammate_ids):
            self.winner_game.increment_score()

        # Refresh the scores of all contestants to get the latest loaded from DB
        self._refresh_all_scores()

        return self._declare_winner_if_game_is_over()


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

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.card} (by {self.player})"

    @cached_property
    def card_obj(self):
        return Card(representation=self.card)


class Trick(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # num is the number trick of the hand (e.g. 1, 2, 3, 4, 5, and then 6)
    num = models.IntegerField()

    hand = models.ForeignKey(Hand, related_name='tricks', on_delete=models.CASCADE, null=True)
    active_player = models.ForeignKey(Player, related_name='tricks_playing', on_delete=models.CASCADE, null=True)
    taker = models.ForeignKey(Player, related_name='tricks_taken', on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (('hand', 'num'),)
        ordering = ['num']

    def __str__(self):
        return f"{', '.join(self.plays.all())} ({self.id})"

    def is_card_invalid_to_play(self, card, player):
        cards = player.get_cards()

        # First check to make sure the player didn't pull a card out of their sleave
        if card not in cards:
            return f"{card.pretty} is not one of the player's cards"

        lead_card = self.get_lead_play().card_obj if self.get_lead_play() else None
        # If this is the first card, it's valid
        if lead_card is None:
            return

        # If trump was lead, did they follow suit if able?
        has_trump = any(c.is_trump(self.hand.trump) for c in cards)
        if lead_card.is_trump(self.hand.trump) and not card.is_trump(self.hand.trump) and has_trump:
            return "must follow suit"

        # For other lead suits, ensure card is following suit (or player is trumping)
        has_lead_suit = any(c.suit == lead_card.suit for c in cards)
        if (lead_card.suit != card.suit) and has_lead_suit and not card.is_trump(self.hand.trump):
            return "must follow suit"

        return None

    def submit_card_to_play(self, card, player):
        """Handles validation of the card's legality

        Returns:
            trick_finished (bool): whether or not the trick is finished

        """
        if player != self.active_player:
            raise ValidationError(f"It is not {player}'s turn to play")

        error_msg = self.is_card_invalid_to_play(card, player)
        if error_msg:
            raise ValidationError(f"Unable to play {card.pretty} ({error_msg}), please choose another card")

        LOG.info(f"{player} played {card}")
        self.active_player = self.hand.game.next_player(self.active_player)
        self.save()

        # Officially "play" the card, if the play hasn't already been created in the view
        play, created = Play.objects.get_or_create(
            card=card.to_representation(),
            player=player,
            trick=self,
        )

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
                card_to_play = self.active_player.play_card(self)
                trick_finished = self.submit_card_to_play(card_to_play, self.active_player)
            else:
                # Waiting for a human to play, just return
                return

        self._finalize_trick()

    def _find_winning_play(self):
        plays = list(self.plays.all())
        current_high = plays[0]
        for play in plays[1:]:
            if current_high.card_obj.is_less_than(play.card_obj, self.hand.trump):
                current_high = play
        return current_high

    def _award_cards_to_taker(self):
        winning_play = self._find_winning_play()
        LOG.info(f"Winning play was {winning_play}")
        self.taker = winning_play.player
        cards = self.get_cards()

        # Give games points to taker
        game_points = sum(card.game_points for card in cards)
        self.taker.current_hand_game_points_won = F('current_hand_game_points_won') + game_points
        self.taker.save()

        # Award Jack or Jick, if taken
        jack = next((card for card in cards if card.is_jack(self.hand.trump)), None)
        jick = next((card for card in cards if card.is_jick(self.hand.trump)), None)
        if jack:
            self.hand.winner_jack = self.taker
            LOG.info(f"{self.taker} won Jack ({jack})")
        if jick:
            self.hand.winner_jick = self.taker
            LOG.info(f"{self.taker} won Jick ({jick})")
        if jick or jack:
            self.hand.save()

    def _finalize_trick(self):
        self.active_player = None
        self._award_cards_to_taker()
        LOG.info(f"Trick is finished. {self.taker} took the following cards: {self.get_cards()}")
        self.save()
        self.hand.advance_hand()

    def player_can_change_play(self, player):
        # TODO - do we want to allow async play submission?
        return False
